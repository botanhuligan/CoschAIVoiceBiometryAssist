import yaml

def clear_text(text):
    return [''.join(list(filter(lambda letter: letter.isalpha(), w)))
            for w in text.lower().split()]


def read_yaml(file):
    with open(file, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            return None
