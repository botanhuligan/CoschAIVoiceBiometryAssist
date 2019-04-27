from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["POST", "GET"])
def index():
    args = {"method": "GET"}
    return render_template("index.html", args=args)


@app.route("/speak", methods=["POST"])
def recognize_google():
    try:
        file = request.files["file"]
    except Exception as e1:
        pass


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



