import logging

import requests
from app.tts.config import VOICE_CODE, TTS_URL

logger = logging.getLogger("SERVER")

def make_speak(text: str, file_path:str):

    logger.debug("Try to send to TTS: " + str(text))
    r = requests.get(TTS_URL, json={'phrase': text, 'voice': VOICE_CODE})
    if r.status_code == 200:
        logger.debug("TTS status code OK")
        with open(file_path, 'wb') as outfile:
            outfile.write(r.content)
        logger.debug('TTS: speech result in "' + file_path + '"')
        return True
    else:
        logger.error("Bad response from TTS: " + str(r.content))
        print("Bad response from TTS: " + str(r.content))
        return False