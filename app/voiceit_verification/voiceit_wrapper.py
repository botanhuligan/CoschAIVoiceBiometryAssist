import enum
import os
from typing import Optional

from voiceit2 import VoiceIt2
import yaml

from app.voiceit_verification.config import *

app = VoiceIt2(KEY, TOKEN)
path = os.path.join(os.path.dirname(os.path.abspath(__file__)))


class VerificationStatus(enum.Enum):
    SUCC = 1,
    FAIL = 2,


def parse_verification_response(response: dict):
    """
    Парсит ответ от Voiceit API
    :param response:
    :return:
    """
    response_code = response.get("responseCode")
    if response_code == "SUCC":
        return VerificationStatus.SUCC
    return VerificationStatus.FAIL


def verify_user(user_name: str, file: str) -> VerificationStatus:
    """
    Проводит верификацию пользователя по имени
    :param user_name: имя пользователя
    :param file: путь к файлу с записью голоса для верификации
    :return:
    """
    user_id = get_user_id(user_name)
    assert user_id
    return parse_verification_response(
        app.voice_verification(user_id, LANG, VERIFICATION_PHRASE, file)
    )


def add_voice_snapshot(user_name: str, *files: str):
    """
    Создает слепок для пользователя по его имени
    :param user_name: имя пользователя
    :param files: пути к файлам для создания слепка
    :return:
    """
    assert len(files) > 0
    user_id = get_user_id(user_name)
    assert user_id
    for file in files:
        app.create_voice_enrollment(user_id, LANG, VERIFICATION_PHRASE, file)


def add_new_user(user_name: str):
    """
    Создает нового пользователя с указанными именем без слепка
    :param user_name:
    :return:
    """
    users = yaml.safe_load(open(path + "/users.yaml"))
    if not users:
        users = {}
    if user_name in users:
        raise KeyError("Этот пользователь уже существует")
    response = app.create_user()
    try:
        user_id = response['userId']
        with open(path + "/users.yaml", "a") as f:
            f.write("%s: %s" % (user_name, user_id))
    except KeyError:
        print("Не удалось создать пользователя")


def delete_user(user_name: str):
    """
    Удаляет пользователя по имени
    :param user_name:
    :return:
    """
    users = yaml.safe_load(open(path + "/users.yaml"))
    to_drop_id, to_drop_name = None, None
    if not users:
        return
    for _name, _id in users.items():
        if _name != user_name:
            pass
        else:
            to_drop_name = _name
            to_drop_id = _id
    if to_drop_id:
        del users[to_drop_name]
        app.delete_user(to_drop_id)
    with open(path + "/users.yaml", "w") as f:
        for _name, _id in users.items():
            f.write("%s: %s" % (_name, _id))


def get_user_id(user_name: str) -> Optional[str]:
    users = yaml.safe_load(open(path + "/users.yaml"))
    if not users:
        return
    return users.get(user_name)


def audio(name: str, ext="wav"):
    return path + "/audio/%s.%s" % (name, ext)


if __name__ == "__main__":
    delete_user("sasha")
    add_new_user("sasha")

    _dir = "/Users/einstalek/app_server/voiceit_verification/audio/"
    add_voice_snapshot("sasha",
                       _dir + "sasha.1.wav",
                       _dir + "sasha.2.wav",
                       _dir + "sasha.3.wav")

    print(
        verify_user("sasha", _dir + "sasha.test.wav")
    )
