#!/usr/bin/env python3

# NOTE: this example requires PyAudio because it uses the Microphone class

from pathlib import Path
import speech_recognition as sr


class AudioRecognizer():
    recognizer = None

    def get_audio(self,path):
        self.recognizer = sr.Recognizer()
        with sr.AudioFile(path) as source:
            audio = self.recognizer.record(source)  # read the entire audio file
            return audio

    def recognize_google(self, audio):
        self.recognizer = sr.Recognizer()
        try:
            result =  self.recognizer.recognize_google(audio, language="ru-RU")
            return result
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))




if __name__ == "__main__":
    mc = AudioRecognizer()
    print("Google thinks you said " + mc.recognize_google())
