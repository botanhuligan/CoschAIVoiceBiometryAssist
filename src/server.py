from flask import Flask, render_template, request
import traceback

app = Flask(__name__)


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
    except Exception as exception:
        print("EXCEPTION in recognize: ", exception)
        traceback.print_exc()


@app.route("/text", methods=["GET"])
def get_text():
    try:
        text = request.args.get("text")
        answer = "ответ"
        args = {"method": "GET"}
        return render_template("text.html", question=text, answer=answer, args=args)
    except Exception as exception:
        print("EXCEPTION in get_text: ", exception)
        traceback.print_exc()
