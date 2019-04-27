import enum
import os
from voiceit2 import VoiceIt2
from voiceit_verification.config import *

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


def verify_user(user: str, file: str) -> VerificationStatus:
    """
    Проводит верификацию пользователя по VoiceitID
    :param user: ID пользователя
    :param file: путь к файлу с записью голоса для верификации
    :return:
    """
    return parse_verification_response(
        app.voice_verification(user, LANG, VERIFICATION_PHRASE, file)
    )


def add_voice_snapshot(user: str, *files: str):
    """
    Создает слепок для пользователя с VoiceitID
    :param user: ID пользователя
    :param files: пути к файлам для создания слепка
    :return:
    """
    assert len(files) > 0
    for file in files:
        return app.create_voice_enrollment(user, LANG, VERIFICATION_PHRASE, file)


def audio(name: str, ext="wav"):
    return path + "/audio/%s.%s" % (name, ext)


if __name__ == "__main__":
    # Creating snapshot
    files = [audio("sasha.1"), audio("sasha.2"), audio("sasha.3")]
    result = add_voice_snapshot(users.get("sasha"), *files)

    # Verifying user
    # SUCC
    print(
        verify_user(users.get("sasha"), path + "/audio/sasha.test.wav")
    )

    # FAIL
    print(
        verify_user(users.get("sasha"), path + "/audio/gosha.test.wav")
    )

