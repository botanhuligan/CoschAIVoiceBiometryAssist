import yaml
import re

def clear_text(text):
    text = text.replace('ё','е')
    text = " ".join([w for w in re.split("\W", text) if w])
    return [''.join(list(filter(lambda letter: letter.isalpha(), w)))
            for w in text.lower().split()]


def read_yaml(file):
    with open(file, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            return None


# функция возвращает произвольную фразу из списка - для более живого общения :)
def random_from_list(list_: list) -> str:
    import random
    secure_random = random.SystemRandom()
    return secure_random.choice(list_)
