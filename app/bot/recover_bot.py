from enum import Enum
import random
from random import randint
import os

# from bot.parser import ParseTypes, Parser
# from bot.util import clear_text, read_yaml
from app.bot.parser import ParseTypes, Parser
from app.bot.util import clear_text, read_yaml
from app.voiceit_verification.voiceit_wrapper import (
    verify_user,
    VerificationStatus
)

data_path = os.path.dirname(os.path.abspath(__file__)) + "/data/"
CHECK_WORDS_AMOUNT = 3

class States(Enum):
    INIT = "INIT"
    NAME = "NAME"
    READY = "READY"
    PHRASE = "PHRASE"
    DONE = "DONE"
    CHECK_KEY_WORDS = "CHECK_KEY_WORDS"


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
            return "Хорошо, Вы готовы восстановить ключ?"
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

    def message(self, text, uid, voice_file = None):
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

                # TODO: убрать, когда файлы будут всегда
                if not voice_file:
                    words = self.get_words(session.get_name())
                    session.set_state(States.CHECK_KEY_WORDS)
                    return "Правильно распознанная фраза! А теперь выбери свои ключевые слова: " \
                           "{0}".format(words)

                elif verify_user(session.get_name(), voice_file) == VerificationStatus.SUCC:
                    session.set_state(States.CHECK_KEY_WORDS)
                    words = self.get_words(session.get_name())
                    return "Правильно распознанная фраза! А теперь выбери свои ключевые слова: " \
                           "{0}".format(words)
                else:
                    session.set_state(States.DONE)
                    return "К сожалению, биометрия не пройдена."
            session.set_state(States.PHRASE)
            return "Плохо, давай ещё: " + session.get_phrase()
        elif state == States.CHECK_KEY_WORDS:
            if self.check_key_words(text, session.get_name()):
                session.set_state(States.DONE)
                return "Отлично, вы сохраняли: {0}".format(self.get_saved(session.get_name()))
            else:
                session.set_state(States.DONE)
                return "Увы, но слова найдены неверно. В доступе отказано."
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

    def key_words(self, name):
        base = read_yaml(data_path + "persona.yaml")
        return base[name]

    def check_key_words(self, text, name):
        tokens = clear_text(text)
        kw = self.key_words(name)
        for token in tokens:
            if token not in kw:
                return False
        return True

    def get_words(self, name):
        words = []
        key_words = self.key_words(name)
        key_pos = random.sample(range(0, len(key_words) - 1), CHECK_WORDS_AMOUNT)
        pos_in_phrase = random.sample(range(0, 20), CHECK_WORDS_AMOUNT)
        with open(data_path + "word.txt", "r") as file:
            text = clear_text(file.read().replace("\n", " "))
            text = [word for word in text if len(word) > 3]
        words_pos = random.sample(range(0, len(text)-1), 20-CHECK_WORDS_AMOUNT)

        key = 0
        other = 0

        for ind, pos in enumerate(words_pos):
            if ind in pos_in_phrase:
                words.append(key_words[key_pos[key]])
                print(key_words[key_pos[key]])
                key += 1
            else:
                words.append(text[words_pos[other]])
                other += 1
        return words

    def get_saved(self, name):
        base = read_yaml(data_path + "saved.yaml")
        return base[name] if name in base else None


if __name__ == "__main__":
    bot = RecoverBot()
    print(bot.start("123", "виталий"))
    while True:
        print("================")
        text = input("INPUT::")
        answ = bot.message(text, "123")
        if not answ:
            break
        print("OUTPUT:: " + str(answ))

