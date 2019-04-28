import re
from enum import Enum
# from bot.util import read_yaml
from app.bot.util import read_yaml
from pymorphy2 import MorphAnalyzer

morph = MorphAnalyzer()


class ParseTypes(Enum):
    NAME = "NAME"
    READY = "READY"
    APPROVE = "APPROVE"
    KEY = "KEY"
    WRONG_NAME = "WRONG_NAME"


class Parser:

    def __init__(self, path):
        self._model = read_yaml(path)

    def _parse(self, text, parse_type):
        if parse_type.value in self._model:
            for pattern in self._model[parse_type.value]:
                regex_res = re.findall(pattern, text)
                if regex_res:
                    print(regex_res[0])
                    return regex_res[0]
        return None

    def parse(self, text, parse_type=None):
        if not self._model:
            print("EXCEPTION:: NO MODEL IN PARSER")
            return None

        if parse_type in ParseTypes:
            return self._parse(text, parse_type)

        return None

    @staticmethod
    def extract_name(text):
        name, surname, patr = None, None, None
        words = [w for w in re.split("\W", text) if w]
        for w in words:
            tag = morph.parse(w)[0].tag
            if "Name" in tag:
                name = w
            elif "Surn" in tag:
                surname = w

        if not name and not surname:
            return None
        return "%s %s" % (surname, name)


