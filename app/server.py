import uuid

from flask import Flask, render_template, request, make_response
import traceback
from bot import DomainBot

app = Flask(__name__)
app.secret_key = "SECRET_KEY"
bot = DomainBot()

active_users = []


def __log_text(uid, msg, answ):
    print("\nUSER:: {0}\nMESSAGE:: {1} \nANSWER:: {2} \n".format(uid, msg, answ))


def add_user(uid):
    active_users.append(uid)
    print("USER {0} ADDED".format(uid))


@app.route("/", methods=["POST", "GET"])
def index():
    args = {"method": "GET"}
    return render_template("index.html", args=args)


@app.route("/voice", methods=["POST"])
def recognize():
    try:
        file = request.files["file"]
        if file:
            print("got file")
        # file to stt
        # text to bot
        # bot text to tts
    except Exception as exception:
        print("EXCEPTION in recognize: ", exception)
        traceback.print_exc()


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
