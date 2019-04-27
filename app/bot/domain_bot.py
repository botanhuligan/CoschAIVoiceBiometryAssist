import os
from enum import Enum

# from bot.new_person_bot import NewPerson
# from bot.parser import Parser, ParseTypes
# from bot.recover_bot import RecoverBot
from app.bot.new_person_bot import NewPerson
from app.bot.parser import Parser, ParseTypes
from app.bot.recover_bot import RecoverBot

data_path = os.path.dirname(os.path.abspath(__file__)) + "/data/"


class States(Enum):
    INIT = "INIT"
    PROBLEM = "PROBLEM"
    IS_NEW = "IS_NEW"
    DONE = "DONE"
    EXIT_DONE = "EXIT_DONE"
    NEW_PERSON = "NEW_PERSON"
    RECOVER_KEY = "RECOVER_KEY"
    WRONG_NAME = "WRONG_NAME"


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


class DomainBot:
    """
    Ведёт общение с пользователем
    """

    def __init__(self):
        self._session = {}
        self._parser = Parser(data_path + "model.yaml")
        self._new_person = NewPerson()
        self._recover_bot = RecoverBot()

    def start(self, uid):
        session = Session()
        session.set_state(States.INIT)
        self._session[uid] = session
        return "Здравствуйте! Представьтесь, пожалуйста!"

    def _set_state(self, uid, state):
        self._session[uid].set_state(state)

    def set_name(self, text, uid):
        session = self._session[uid]
        name = self._parser.parse(text, ParseTypes.NAME)
        session.set_name(name if name else text)
        name = name if name else text
        return name

    def ready(self, text):
        return self._parser.parse(text, ParseTypes.READY)

    def message(self, text, uid, voice_file = None):
        if uid not in self._session:
            print("NEW MESSAGE FROM UNRECOGNIZED USER {0}".format(uid))
            return self.start(uid)

        session = self._session[uid]
        state = session.get_state()
        print("STATE: {}".format(session.get_state()))

        if state == States.DONE:
            session.set_state(States.EXIT_DONE)
            return "Я могу Вам ещё чем-то помочь?"

        elif state == States.EXIT_DONE:
            approve = self._parser.parse(text, ParseTypes.APPROVE)
            if approve:
                session.set_state(States.PROBLEM)
                return "Чем я могу помочь, {0}?".format(session.get_name())
            else:
                session.set_state(States.DONE)
                return "Хорошо."

        elif state == States.INIT:
            name = self.set_name(text, uid)
            session.set_state(States.PROBLEM)
            return "Хорошо, {0}! Что у вас случилось?".format(name)

        elif state == States.PROBLEM:
            is_name = self._parser.parse(text, ParseTypes.WRONG_NAME)
            if is_name:
                session.set_state(States.INIT)
                return "Хорошо, уточните, как Вас зовут?"
            key = self._parser.parse(text, ParseTypes.KEY)
            if key:
                session.set_state(States.RECOVER_KEY)

                return self._recover_bot.start(uid, session.get_name())

            session.set_state(States.IS_NEW)
            return "Вы хотите завести нового пользователя?"

        elif state == States.IS_NEW:
            approve = self._parser.parse(text, ParseTypes.APPROVE)
            if approve:
                session.set_state(States.NEW_PERSON)
                return self._new_person.start(uid, session.get_name())

        elif state == States.NEW_PERSON:
            result = self._new_person.message(text, uid)
            if result:
                return result
            else:
                session.set_state(States.DONE)
                return "Я рад, что смог Вам помочь!"

        elif state == States.RECOVER_KEY:
            result = self._recover_bot.message(text, uid)
            if result:
                return result
            else:
                session.set_state(States.DONE)
                return "Я рад, что смог Вам помочь!"

        name = session.get_name()
        if name:
            session.set_state(States.PROBLEM)

            return "Что случилось, {0}?".format(name)

        session.set_state(States.INIT)
        return "Уточните, пожалуйста, как Вас зовут."


if __name__ == "__main__":
    bot = DomainBot()
    print(bot.start("123"))
    while True:
        print("================")
        text = input("INPUT::")
        print("OUTPUT:: " + str(bot.message(text, "123")))
