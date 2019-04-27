import os
from enum import Enum
import yaml
# from bot.parser import Parser, ParseTypes
# from bot.util import clear_text, read_yaml
from app.bot.parser import Parser, ParseTypes
from app.bot.util import clear_text

WORDS_AMOUNT = 5
data_path = os.path.dirname(os.path.abspath(__file__)) + "/data/"


class Session:
    def __init__(self):
        self.words = []
        self.status = ""
        self.name = ""

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_words(self):
        return self.words

    def get_status(self):
        return self.status

    def set_words(self, words):
        self.words = words

    def set_status(self, status):
        self.status = status


class Status(Enum):
    WAITING_WORDS = "WAITING_WORDS"
    WAITING_FOR_APPROVE = "WAITING_FOR_APPROVE"
    SAVE = "SAVE"


class NewPerson:

    def __init__(self):
        self._session = {}
        self._parser = Parser(data_path + "model.yaml")
        self._person_path = data_path + "persona.yaml"
        self._secret_path = data_path + "saved.yaml"

    def start(self, uid, name):
        self._session[uid] = Session()
        self._session[uid].set_name(name)
        self._session[uid].set_status(Status.WAITING_WORDS)
        return "Назовите, пожалуйста, {} ключевых слов".format(WORDS_AMOUNT)

    def message(self, text, uid):

        if uid not in self._session:
            print("NewPerson::MESSAGE FROM UNRECOGNIZED USER {0}".format(uid))
            return None

        session = self._session[uid]
        if session.get_status() == Status.WAITING_WORDS:
            words = clear_text(text)
            if len(words) == WORDS_AMOUNT:
                if self.is_repeatable(words):
                    return "Слова должны быть уникальны, повторите пожалуйста."
                session.set_words(words)
                session.set_status(Status.WAITING_FOR_APPROVE)
                if any([len(word) > 3 for word in words]):
                    return "Я правильно понял, что Вы хотите использовать ключевыми слова: {}".format(", ".join(words))
                else:
                    return "К сожалению, слова не должны быть короче 4х букв. Повторите, пожалуйста."
            else:
                return "Неверное количество слов, повторите пожалуйста."

        elif session.get_status() == Status.WAITING_FOR_APPROVE:
            approved = self._parser.parse(text, ParseTypes.APPROVE)
            if approved:
                self.save(session.get_name(), session.get_words())
                session.set_status(Status.SAVE)
                return "Добавил! А теперь скажите, что сохранить?"
            self.end(uid)
            return "Хорошо, отменяю сохранение ключевых слов. Обращайся, если понадоблюсь!"

        elif session.get_status() == Status.SAVE:
            self.save_secret(session.get_name(), text)
            self.end(uid)
            return "Сохранено"

        return "Не совсем понял, как мы тут оказались"

    def end(self, uid):
        self._session.pop(uid)

    def save(self, name, words):
        person = read_yaml(self._person_path)

        if not person:
            person = {}
        person[name] = words

        try:
            with open(self._person_path, 'w') as stream:
                yaml.safe_dump(person, stream)
        except yaml.YAMLError as exc:
            print(exc)
            return None

    def save_secret(self, name, phrase):
        person = read_yaml(self._secret_path)

        if not person:
            person = {}
        person[name] = phrase

        try:
            with open(self._secret_path, 'w') as stream:
                yaml.safe_dump(person, stream)
        except yaml.YAMLError as exc:
            print(exc)
            return None

    @staticmethod
    def is_repeatable(lst):
        for ind, word in enumerate(lst):
            if ind != len(lst) - 1:
                if word in lst[ind+1:len(lst)-1]:
                    return True
        return False


if __name__ == "__main__":
    bot = NewPerson()
    print(bot.start("123", "виталий"))
    while True:
        print("================")
        text = input("INPUT::")
        answ = bot.message(text, "123")
        if not answ:
            break
        print("OUTPUT:: " + str(answ))
