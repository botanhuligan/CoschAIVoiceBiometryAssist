from enum import Enum
from random import randint
import os

from src.bot.parser import ParseTypes, Parser

data_path = os.path.dirname(os.path.abspath(__file__)) + "/data/"


class States(Enum):
    INIT = "INIT"
    NAME = "NAME"
    READY = "READY"
    PHRASE = "PHRASE"


class Bot:
    def __init__(self):
        self._session = {}
        self._parser = Parser(data_path + "model.yaml")

    def start(self, text, uid):
        self._session[uid] = {}
        self._session[uid]["state"] = States.INIT
        return "Здравствуйте! Что у вас случилось?"

    def set_name(self, text, uid):
        if "name" not in self._session[uid]:
            name = self._parser.parse(text, ParseTypes.NAME)
            self._session[uid]["name"] = name if name else text

        self._session[uid]["state"] = States.READY
        return self._session[uid]["name"]

    def ready(self, text):
        return self._parser.parse(text, ParseTypes.READY)

    def message(self, text, uid):
        if uid not in self._session:
            print("NEW MESSAGE FROM UNRECOGNIZED USER {0}".format(uid))
            return self.start(text, uid)

        state = self._session[uid]["state"]
        if state == States.INIT:
            self._session[uid]["state"] = States.NAME
            return "Привет! Я с радостью помогу тебе! Представься, пожалуйста."

        elif state == States.NAME:
            name = self.set_name(text, uid)
            return "И снова здравствуй, {0}! Ты готов восстановить ключ?".format(name)

        elif state == States.READY:
            if self.ready(text):
                self._session[uid]["state"] = States.PHRASE
                phrase = self.generate_phrase()
                return "Произнесите, пожалуйста, громко вслух фразу: " + phrase
            else:
                return 'Хорошо. Скажите "готов", как будете готовы'

        self._session[uid]["state"] = States.NAME
        return "Кажется, Вы потерялись. Начнём сначала? Представься, пожалуйста."

    @staticmethod
    def generate_phrase():
        with open(data_path + "phrases.txt", "r") as file:
            phrases = file.readlines()
            number = randint(0, len(phrases)-1)
            return phrases[number]



