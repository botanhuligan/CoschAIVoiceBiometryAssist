import requests
VOICE_CODE = 'ru-RU-Wavenet-D'
TTS_URL = 'http://ec2-52-17-228-123.eu-west-1.compute.amazonaws.com:8889/speech_google'

def make_speak(text: str, file_path:str):

    print("Try to send to TTS: " + str(text))
    r = requests.get(TTS_URL, json={'phrase': text, 'voice': VOICE_CODE})
    if r.status_code == 200:
        with open(file_path, 'wb') as outfile:
            outfile.write(r.content)
        print('TTS: speech result in "' + file_path + '"')
        return True
    else:
        print("Bad response from TTS: " + str(r.content))
        return False