import uuid, os

from flask import Flask, render_template, request, make_response, \
    Response, send_file, url_for, redirect
import traceback
from .bot import DomainBot
from .stt.recognizer import AudioRecognizer
from .tts.speaker import make_speak

app = Flask(__name__)
app.secret_key = "SECRET_KEY"
bot = DomainBot()

active_users = []

# key - uid, value - response dict
WAIT_RESPONCES = {}

THIS_FILE_PATH = os.path.dirname(os.path.abspath(__file__))


def __save_wav(name, file_bytes):
    complete_path = os.path.join(THIS_FILE_PATH + '/wavs/'+ name)
    file1 = open(complete_path, "wb")
    file1.write(file_bytes)
    file1.close()

def __recognize(file_name: str) -> str:
    # use the audio file as the audio source
    try:
        recognizer = AudioRecognizer()
        audio = recognizer.get_audio(THIS_FILE_PATH + '/wavs/'+file_name)
        print('Найден файл: '+str(type(audio)))
        text = recognizer.recognize_google(audio)
        print('Текст распознан:' + text)
        return text
    except Exception as e:
        print('Recognizer exception: '+str(e))
        return None

def __get_voice(text:str) -> str:
    file_name = str(text).lower().strip() + '.wav'
    file_path = THIS_FILE_PATH + '/audio/' + file_name
    exists = os.path.isfile(file_path)
    if exists:
        print('Voice already exist')
    else:
    # Keep presets
        make_speak(text, file_path)
    return file_path


def __log_text(uid, msg, answ):
    print("\nUSER:: {0}\nMESSAGE:: {1} \nANSWER:: {2} \n".format(uid, msg, answ))


def add_user(uid):
    active_users.append(uid)
    print("USER {0} ADDED".format(uid))

def save_response_and_get_voice(uid:str,
                                input_phrase,
                                response_to_say,
                                text_to_show,
                                meta:dict={}) -> str:
    voice_file_path = __get_voice(response_to_say)
    response = {
        "input_phrase": input_phrase, "text_to_show": text_to_show, "meta":meta
    }
    WAIT_RESPONCES[uid] = response
    return voice_file_path

def get_wait_responce(uid:str)->dict:
    if uid in WAIT_RESPONCES.keys() and WAIT_RESPONCES[uid] is not None:
        result = WAIT_RESPONCES[uid]
        WAIT_RESPONCES[uid] = None
        return result
    else:
        return {}


# page with api description
@app.route("/", methods=["POST", "GET"])
def index():
    args = {"method": "GET"}
    return render_template("index.html", args=args)


@app.route("/start", methods=["POST"])
def handle_start():
    uid = str(uuid.uuid4())
    add_user(uid)
    is_set_cookie = True
    answer = bot.start(uid)


# return voice.mp3 and save text info for gui
@app.route("/voice", methods=["POST"])
def handle_voice():

    try:
        # get or generate uid
        uid = str(request.cookies.get('userID'))
        if uid is None:
            return redirect(url_for('start'))

        # save wav file
        file_name = str(uuid.uuid4())+'.wav'
        try:
            file = request.files["file"]
            __save_wav(file_name, file.read())
        except Exception as exception:
            print(str(exception))
            file = request.data
            __save_wav(file_name, file)

        # send to recognition
        recognition_result = __recognize(file_name)

        if recognition_result is None:
            # push message to voice bot
            answer = bot.message(recognition_result, uid, file_name)
            voice_file = save_response_and_get_voice(uid, '', answer, answer)
        else:
            voice_file = save_response_and_get_voice(uid, '', 'Повторите, Вас плохо слышно', 'Повторите, Вас плохо слышно')

        send_file(voice_file)
        return recognition_result
    except Exception as e:
        print('Exception in recognize_google: ' + str(e))
        return Response(status=500, response = 'Exception in voice handler: '+ str(e))


@app.route("/text", methods=["GET"])
def get_text():
    try:
        text = str(request.args.get("text"))
        uid = str(request.cookies.get('userID'))
        is_set_cookie = False
        print(text)
        if uid and uid in active_users:
            answer = bot.message(text, uid)
        else:
            uid = str(uuid.uuid4())
            add_user(uid)
            is_set_cookie = True
            answer = bot.start(uid)
        __log_text(uid, text, answer)

        args = {"method": "GET"}
        resp = make_response(render_template("text.html", question=text, answer=answer, args=args))
        if is_set_cookie:
            resp.set_cookie('userID', uid)
        return resp

    except Exception as exception:
        print("EXCEPTION in get_text: ", exception)
        traceback.print_exc()
