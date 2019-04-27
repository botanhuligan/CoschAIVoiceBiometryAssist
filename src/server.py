from flask import Flask, render_template, request
import traceback

app = Flask(__name__)


@app.route("/", methods=["POST", "GET"])
def index():
    args = {"method": "GET"}
    return render_template("index.html", args=args)


@app.route("/speak", methods=["POST"])
def recognize_google():
    try:
        file = request.files["file"]
        if file:
            print("got file")
    except Exception as exception:
        print("EXCEPTION: ", exception)
        traceback.print_exc()


@app.route("/text", methods=["GET"])
def get_text():
    text = request.args.get("text")
    answer = "ответ"
    args = {"method": "GET"}
    
    return render_template("text.html", question=text, answer=answer, args=args)

# @app.route("/download_results", methods=["GET"])
# def download_results ():
#     try:
#         zip_name = 'wavs.zip'
#         zip_dir('wavs', zip_name)
#         zeroize_results()
#         return send_file(THIS_FILE_PATH +"/"+zip_name, as_attachment=True)
#     except Exception as e:
#         print('Exception in download_results: '+ str(e))
#         return Response(status=500, response = 'Exception in download_results: '+ str(e))



