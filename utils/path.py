from pathlib import Path


def get_root_dir() -> Path:
    return Path(__file__).parent.parent


def to_dash_case(text):
    text = text.lower()
    temp = text.split(' ')
    for x in range(len(temp)):
        temp[x] = ''.join(e for e in temp[x] if e.isalnum())
    text = '_'.join(temp)

    return text
