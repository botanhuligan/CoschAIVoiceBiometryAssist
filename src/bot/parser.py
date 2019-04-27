import re
from enum import Enum
from src.bot.util import read_yaml


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
