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


def get_file_name(filename):
    split_file = filename.split('.')
    return ''.join(split_file[0:len(split_file) - 1])


def get_ext(filename):
    split_file = filename.split('.')
    return split_file[len(split_file) - 1]