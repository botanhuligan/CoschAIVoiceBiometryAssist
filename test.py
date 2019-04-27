from app.tts.speaker import make_speak
import os
THIS_FILE_PATH = os.path.dirname(os.path.abspath(__file__))

def test_tts():
    test_file_path = THIS_FILE_PATH+'/test.mp3'
    make_speak('Привет! Я знаю часть твоего секрета', test_file_path)
    size = os.path.getsize(test_file_path)
    if size == 0:
        print("Voice not created!!!")
    else:
        print('Voice create ok')

test_tts()