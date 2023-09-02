import sys

from src.services.detik import scrap as detik_scrap
from src.services.pikiran_rakyat import pikiran_rakyat_scrap


def prompt_menu():
    print('Menu:')
    print('0. Stop Application')
    print('1. Scrap Detik')
    print('2. Scrap Pikiran Rakyat')

    return input('Choose which media you wanna scrap for: ')


def main():
    menu = '-1'
    while menu != '0':
        menu = sys.argv[1] if 1 < len(sys.argv) else prompt_menu()

        keyword = sys.argv[2] if 2 < len(sys.argv) else input('Keyword: ')
        page_number = sys.argv[3] if 3 < len(sys.argv) else input('How many pages? (number): ')

        if len(sys.argv) < 4:
            print('\n\nWhen you fill folder name, it will make your scrapping data only go to that folder')
            print('The advantage is, it will matching the upcoming scrapping data id with the old data id on that folder')
            print('The id is a conversion from title -> lowercased -> remove unnecessary punctuation -> change space to '
                  'underscore\n\n')
            print('default = {timestamp}')
        folder_input = sys.argv[4] if 4 < len(sys.argv) else input('Folder name: ')
        folder: None | str = None
        if folder_input != '':
            folder = folder_input

        match menu:
            case "0":
                print('Application stopped')
            case "1":
                detik_scrap(keyword, page_number, folder)
            case "2":
                pikiran_rakyat_scrap(keyword, page_number, folder)
            case _:
                print('Please input the correct menu')

        if len(sys.argv) > 1:
            menu = '0'


main()
