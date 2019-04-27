import requests
VOICE_CODE = ''
TTS_URL = ''

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