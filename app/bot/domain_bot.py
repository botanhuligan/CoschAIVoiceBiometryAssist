import os, uuid, logging
from enum import Enum

from app.bot.new_person_bot import NewPerson
from app.bot.parser import Parser, ParseTypes
from app.bot.recover_bot import RecoverBot
# from app.voiceit_verification.voiceit_wrapper import add_new_user as add_new_user_voice_bio, add_voice_snapshot
from app.bot.util import random_from_list
from app.gmm_verification.gmm_model import add_voice_snapshot

data_path = os.path.dirname(os.path.abspath(__file__)) + "/data/"

logger = logging.getLogger("DOMAIN_BOT")

TRUE_NEXT_STATE = None

class States(Enum):
    INIT = "INIT"
    PROBLEM = "PROBLEM"
    IS_NEW = "IS_NEW"
    DONE = "DONE"
    EXIT_DONE = "EXIT_DONE"
    NEW_PERSON = "NEW_PERSON"
    RECOVER_KEY = "RECOVER_KEY"
    WRONG_NAME = "WRONG_NAME"

    BOLTALKA = "BOLTALKA"
    END_BOLTALKA = "END_BOLTALKA"


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
        return random_from_list(["Здравствуйте!", 'Привет'])+ "Здесь я могу вернуть Ваш секрет, " \
               "если Вы пройдете голосовую и диалоговую биометрию." + \
               random_from_list(["Назовите имя и фамилия?", 'Скажите Ваше имя и фaмилию'])

    def _set_state(self, uid, state):
        self._session[uid].set_state(state)

    def set_name(self, text, uid):
        session = self._session[uid]
        extracted_name = self._parser.extract_name(text)
        if extracted_name:
            name = extracted_name
        else:
            name = self._parser.parse(text, ParseTypes.NAME)
        session.set_name(name if name else text)
        name = name if name else text
        return name

    # add user without dialog
    def add_new_user(self, uid, name, words, voice_file_path):
        try:
            # create voice snapshot
            # add_new_user_voice_bio(name)
            add_voice_snapshot(name, voice_file_path)
            # save new person secret
            self._new_person.start(uid, name)
            self._new_person.save(name, words)
            gen_secret = str(uuid.uuid4())
            self._new_person.save_secret(name, gen_secret)
            # send to biometry
            return gen_secret
        except Exception as e:
            logger.error('Error when add new user: '+str(e))
            return ''

    def ready(self, text):
        return self._parser.parse(text, ParseTypes.READY)

    def message(self, text, uid, voice_file = None):
        global TRUE_NEXT_STATE

        if uid not in self._session:
            logger.debug("NEW MESSAGE FROM UNRECOGNIZED USER {0}".format(uid))
            return self.start(uid)

        session = self._session[uid]
        state = session.get_state()
        print("STATE: {}".format(session.get_state()))

        if state == States.DONE:
            TRUE_NEXT_STATE = States.EXIT_DONE
            session.set_state(States.BOLTALKA)
            return random_from_list(["Пока-пока!", 'До свидания!'])

        elif state == States.EXIT_DONE:
            approve = self._parser.parse(text, ParseTypes.APPROVE)
            if approve:
                session.set_state(States.PROBLEM)
                return random_from_list(["Что случилось?", 'Чем я могу помочь?'])
            else:
                session.set_state(States.DONE)
                return "Хорошо."

        elif state == States.INIT:
            set_name = self.set_name(text, uid)
            name = set_name
            session.set_state(States.PROBLEM)
            return random_from_list(["Что случилось?", 'Чем я могу помочь?'])

        elif state == States.PROBLEM:
            is_name = self._parser.parse(text, ParseTypes.WRONG_NAME)
            if is_name:
                session.set_state(States.INIT)
                return random_from_list(["Чтобы начать, скажите Вашу фамилию и имя",
                                         'Назовите пожалуйста фамилию и имя'])
            # start rocover
            key = self._parser.parse(text, ParseTypes.KEY)
            if key:
                session.set_state(States.RECOVER_KEY)

                return self._recover_bot.start(uid, session.get_name())

            # длбавление пользователя происходит в вебе
            # session.set_state(States.IS_NEW)
            # return "Вы хотите завести нового пользователя?"

        # elif state == States.IS_NEW:
        #     approve = self._parser.parse(text, ParseTypes.APPROVE)
        #     if approve:
        #         session.set_state(States.NEW_PERSON)
        #         return self._new_person.start(uid, session.get_name())
        #
        # elif state == States.NEW_PERSON:
        #     result = self._new_person.message(text, uid)
        #     if result:
        #         return result
        #     else:
        #         session.set_state(States.DONE)
        #         return "Я рад, что смог Вам помочь!"

        elif state == States.RECOVER_KEY:
            result = self._recover_bot.message(text, uid, voice_file)
            if result:
                return result
            else:
                session.set_state(States.DONE)
                return random_from_list(["Желаю удачи в восстановлении!", 'Всега рада помочь']) +\
                       ". Для расшифрования вашего секрета перейдите на страницу http://0.0.0.0:8081/pages/smart-get.html"

        name = session.get_name()
        if name:
            session.set_state(States.PROBLEM)

            return "Что случилось?"

            session.set_state(States.INIT)
            return random_from_list(["Я вас не поняла!", 'Пожалуйста, повторите'])

        # not main logic dialog boltalka
        elif state == States.BOLTALKA:
            session.set_state(States.END_BOLTALKA)
            return random_from_list(["Давай вечером сходим в бар?",
                                     'Какие автомобили ты любишь?',
                                     'Какие планы на выходные?',
                                     'Ты любишь собак или кошек?']
                                    )
        elif state == States.END_BOLTALKA:
            session.set_state(TRUE_NEXT_STATE)
            return random_from_list(["Ура",
                                     'Это хорошо!',
                                     'А мы похожи',
                                     'Я запомнил']
                                    )


if __name__ == "__main__":
    bot = DomainBot()
    print(bot.start("123"))
    while True:
        print("================")
        text = input("INPUT::")
        print("OUTPUT:: " + str(bot.message(text, "123")))
