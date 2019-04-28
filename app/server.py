import uuid, os, logging

from flask import Flask, render_template, request, make_response, \
    Response, send_file, url_for, redirect, jsonify

import traceback
from app.bot import DomainBot
from app.stt.recognizer import AudioRecognizer
from app.tts.speaker import make_speak

main_component = "VBV_SERVER"
logging.basicConfig(
    format='%(levelname)s: [%(asctime)s.%(msecs)03d] {} %(name)s '
           '%(filename)s:%(funcName)s:%(lineno)s:  %(message)s'.format(main_component),
    datefmt='%Y-%m-%d %H:%M:%S', level="DEBUG")

logger = logging.getLogger("SERVER")


app = Flask(__name__)
app.secret_key = "SECRET_KEY"
bot = DomainBot()

active_users = []

# key - uid, value - response dict
WAIT_RESPONCES = {}

# key - uid, value -dict
# { "name" : ""
#   "words": ['',]
#   "file_path: ""
#}
NEW_USERS = {}

THIS_FILE_PATH = os.path.dirname(os.path.abspath(__file__))


def __save_input_wav(name, file_bytes) -> str:
    complete_path = os.path.join(THIS_FILE_PATH + '/wavs/'+ name)
    file1 = open(complete_path, "wb")
    file1.write(file_bytes)
    file1.close()
    return complete_path

def __recognize(file_name: str) -> str:
    # use the audio file as the audio source
    try:
        recognizer = AudioRecognizer()
        audio = recognizer.get_audio(file_name)
        logger.debug('Найден файл: '+str(type(audio)))
        text = recognizer.recognize_google(audio)
        logger.debug('Текст распознан:' + text)
        return text
    except Exception as e:
        logger.error('Recognizer exception: '+str(e))
        return None

# return path of new voice
def __get_voice(text:str) -> str:
    file_name = str(text).lower().strip() + '.mp3'
    # file_name = file_name.replace('.', '')
    file_path = THIS_FILE_PATH + '/audio/' + file_name
    exists = os.path.isfile(file_path)
    if exists:
        logger.debug('Voice already exist')
    else:
    # Keep presets
        make_speak(text, file_path)
    return file_path


def __log_text(uid, msg, answ):
    logger.debug("\nUSER:: {0}\nMESSAGE:: {1} \nANSWER:: {2} \n".format(uid, msg, answ))


def __add_user_as_active(uid):
    active_users.append(uid)
    logger.debug("USER {0} ADDED".format(uid))

def __save_response_and_get_voice(uid:str,
                                  input_phrase,
                                  response_to_say,
                                  text_to_show,
                                  meta:dict={}) -> str:
    logger.debug('Get voice: '+str(response_to_say))
    voice_file_path = __get_voice(response_to_say)
    response = {
        "input_phrase": input_phrase, "text_to_show": text_to_show, "meta":meta
    }
    logger.debug('New text response: '+str(response))
    WAIT_RESPONCES[uid] = response
    return voice_file_path

def __get_wait_responce(uid:str)->dict:
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

### CREATE USER API ###
@app.route("/add_user/name", methods=["POST"])
def add_user_api_name():
    try:
        try:
            name = request.form['name']
        except Exception as e1:
            json_content = request.get_json()
            if json_content is not None:
                name = json_content.get("name", None)
            if name is None:
                name: str = request.args.get('name', default='')

        # get or generate uid
        uid = request.cookies.get('userID')
        if uid is None or uid == 'None':
            uid = str(uuid.uuid4())
            __add_user_as_active(uid)

        new_user = {}
        new_user['name'] = name
        NEW_USERS[uid] = new_user
        logger.debug("Creat new user object for registration")

        response = make_response(('OK', 200))
        response.headers['Set-Cookie'] = 'userID='+uid
        return response
    except Exception as e:
        logger.error('Exception when add name: '+str(e))
        return Response(status=500, response='Exception when add name: ' + str(e))

@app.route("/add_user/words", methods=["POST"])
def add_user_api_words():
    try:
        try:
            words = request.form['words']
        except Exception as e1:
            json_content = request.get_json()
            if json_content is not None:
                words = json_content.get("words", None)
            if words is None:
                words: str = request.args.get('words', default='')

        # get or generate uid
        uid = request.cookies.get('userID')
        if uid is None:
            return Response(status=500, response='No userID in cookie')

        if uid in NEW_USERS.keys():
            NEW_USERS[uid]['words'] = words
        else:
            return Response(status=500, response='No userID in memory')

        logger.debug("Add words for registration OK: "+str(NEW_USERS[uid]))

        response = make_response(('OK', 200))
        # response.headers['Set-Cookie'] = 'userID=' + uid
        return response
    except Exception as e:
        logger.error('Exception when add words: ' + str(e))
        return Response(status=500, response='Exception when add words: ' + str(e))


@app.route("/add_user/voice", methods=["POST"])
def add_user_api_voice():
    try:
        # get or generate uid
        uid = request.cookies.get('userID')
        if uid is None:
            return Response(status=500, response='No userID in cookie')
        # save wav file
        file_name = str(uuid.uuid4()) + '.wav'
        try:
            file = request.files["file"]
            input_wav_path = __save_input_wav(file_name, file.read())
        except Exception as e1:
            file = request.data
            input_wav_path = __save_input_wav(file_name, file)

        size = os.path.getsize(input_wav_path)
        if size == 0:
            logger.error("Wav not created!!!")
            return Response(status=500, response='Wav not created!')
        else:
            logger.debug('Wav create ok')

        # get or generate uid
        # uid = request.cookies.get('userID')
        if uid is None:
            return Response(status=500, response='No userID in cookie')

        if uid in NEW_USERS.keys():
            NEW_USERS[uid]['file_path'] = input_wav_path
        else:
            return Response(status=500, response='No userID in memory')

        # send to recognition
        recognition_result = __recognize(input_wav_path)

        if recognition_result:
            # save user and push message to voice bot
            user = NEW_USERS[uid]
            logger.debug('Try to add new user: '+str(user))
            gen_secret = bot.add_new_user(uid, user['name'], user['words'], user['file_path'])
            if gen_secret!='':
                text_response = {"gen_secret":gen_secret}
                return jsonify(text_response)

        voice_file = __save_response_and_get_voice(uid, '', 'Повторите, Вас плохо слышно',
                                                   'Повторите, Вас плохо слышно')
        response = make_response(send_file(voice_file, as_attachment=True))
        # response.headers['userID'] = uid
        return response

    except Exception as e:
        logger.error('Exception in add_user voice_verification: ' + str(e))
        return Response(status=500, response='Exception in voice handler: ' + str(e))
### CREATE USER API END ###-


### RESTORE SESSION API ####
# start of restore session
@app.route("/start", methods=["GET"])
def handle_start():
    try:
        uid = str(uuid.uuid4())
        __add_user_as_active(uid)
        answer = bot.start(uid)
        voice_file = __save_response_and_get_voice(uid, '', answer, answer)

        response = make_response(send_file(voice_file, as_attachment=True))
        response.headers['Set-Cookie'] = 'userID='+uid
        return response
    except Exception as e:
        logger.error('Exception in handle_start: ' + str(e))
        return Response(status=500, response='Exception in handle_start: ' + str(e))

@app.route("/get_dialog", methods=["GET"])
def handle_get_text():
    uid = request.cookies.get('userID')
    if uid is None:
        return redirect(url_for('start'))
    text_response = __get_wait_responce(uid)
    return jsonify(text_response)


# return voice.mp3 and save text info for gui
@app.route("/voice", methods=["POST"])
def handle_voice():
    logger.debug('Try handle_voice')
    try:
        # get or generate uid
        uid = request.cookies.get('userID')
        # if uid is None:
        #     logger.debug('Uid is None. Redirect to /start')
        #     return redirect(url_for('start'))
        uid = str(uid)
        # save wav file
        file_name = str(uuid.uuid4())+'.wav'
        try:
            file = request.files["file"]
            input_wav_path = __save_input_wav(file_name, file.read())
        except Exception as exception:
            print(str(exception))
            file = request.data
            input_wav_path = __save_input_wav(file_name, file)

        size = os.path.getsize(input_wav_path)
        if size == 0:
            logger.error("Wav not created!!!")
            return Response(status=500, response='Wav not created!')
        else:
            logger.debug('Wav create ok')

        # send to recognition
        recognition_result = __recognize(input_wav_path)

        if recognition_result:
            # push message to voice bot
            answer = bot.message(recognition_result, uid, input_wav_path)
            voice_file = __save_response_and_get_voice(uid, recognition_result, answer, answer)
        else:
            voice_file = __save_response_and_get_voice(uid, '', 'Повторите, Вас плохо слышно', 'Повторите, Вас плохо слышно')

        response = make_response(send_file(voice_file, as_attachment=True))
        response.headers['userID'] = uid
        return response

    except Exception as e:
        logger.error('Exception in voice answer: '+ str(e))
        return Response(status=500, response = 'Exception in voice handler: '+ str(e))
### RESTORE SESSION API END####


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
            __add_user_as_active(uid)
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
