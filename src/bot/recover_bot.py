from enum import Enum
from random import randint
import os

from src.bot.parser import ParseTypes, Parser
from src.bot.util import clear_text, read_yaml

data_path = os.path.dirname(os.path.abspath(__file__)) + "/data/"


class States(Enum):
    INIT = "INIT"
    NAME = "NAME"
    READY = "READY"
    PHRASE = "PHRASE"
    DONE = "DONE"


class Session:
    def __init__(self):
        self._state = ""
        self._phrase = ""
        self._name = ""

    def set_state(self, state):
        self._state = state

    def set_name(self, name):
        self._name = name

    def set_phrase(self, phrase):
        self._phrase = phrase

    def get_state(self):
        return self._state

    def get_name(self):
        return self._name

    def get_phrase(self):
        return self._phrase


class RecoverBot:
    """
    Ведёт общение с пользователем
    """
    def __init__(self):
        self._session = {}
        self._parser = Parser(data_path + "model.yaml")

    @staticmethod
    def is_name_in_base(name):
        base = read_yaml(data_path + "persona.yaml")
        return name in base

    def start(self, uid, name):
        session = Session()
        if self.is_name_in_base(name):
            session.set_state(States.READY)
            session.set_name(name)
            self._session[uid] = session
            return "{0}, ты готов восстановить ключ?".format(name)
        else:
            return "К сожалению, я не знаю, кто такой {0}. Заведите сначала себе аккаунт.".format(name)

    def _set_state(self, uid, state):
        self._session[uid].set_state(state)

    def set_name(self, text, uid):
        session = self._session[uid]
        name = session.get_name()
        if not name:
            name = self._parser.parse(text, ParseTypes.NAME)
            session.set_name(name if name else text)
            name = name if name else text
        return name

    def ready(self, text):
        return self._parser.parse(text, ParseTypes.READY)

    def message(self, text, uid):
        if uid not in self._session:
            print("HELP_BOT:: MESSAGE FROM UNRECOGNIZED USER {0}".format(uid))
            return None

        session = self._session[uid]
        state = session.get_state()
        print("STATE: {}".format(session.get_state()))

        if state == States.READY:
            if self.ready(text):
                phrase = self.generate_phrase()
                session.set_phrase(phrase)
                session.set_state(States.PHRASE)
                return "Произнесите, пожалуйста, громко вслух фразу: " + phrase
            else:
                return 'Хорошо. Скажите "готов", как будете готовы'

        elif state == States.PHRASE:
            is_phrase = self.check_phrase(text, session.get_phrase())
            if is_phrase:
                session.set_state(States.DONE)
                return "Правильно распознанная фраза"
            session.set_state(uid, States.PHRASE)
            return "Плохо, давай ещё: " + session.get_phrase()

        elif state == States.DONE:
            self.end(uid)
            return "Молодец, красавчик, братуха!"

        session.set_state(States.NAME)
        return "Кажется, Вы потерялись. Начнём сначала? готовы произнести слово?"

    def check_phrase(self, text, phrase):
        text_words = clear_text(text)
        phrase_words = clear_text(phrase)
        for word in phrase_words:
            if word not in text_words:
                return False
        return True

    @staticmethod
    def generate_phrase():
        with open(data_path + "phrases.txt", "r") as file:
            phrases = file.readlines()
            number = randint(0, len(phrases)-1)
            return phrases[number]

    def end(self, uid):
        self._session.pop(uid)


if __name__ == "__main__":
    bot = RecoverBot()
    print(bot.start("", "123"))
    while True:
        print("================")
        text = input("INPUT::")
        print("OUTPUT:: " + bot.message(text, "123"))

