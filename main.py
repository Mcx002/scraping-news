import sys

from src.services.detik import detik_scrape
from src.services.kompas import kompas_scrape
from src.services.pikiran_rakyat import pikiran_rakyat_scrape
from src.services.cnn_indonesia import cnn_indonesia_scrape
from src.services.tribunnews import tribunnews_scrape


def prompt_menu():
    print('Menu:')
    print('0. Stop Application')
    print('1. Scrape Detik')
    print('2. Scrape Pikiran Rakyat')
    print('3. Scrape CNN Indonesia')
    print('4. Scrape Tribunnews (limited 11 pages)')
    print('5. Scrape Kompas (limited 11 pages)')

    return input('Choose which media you wanna scrap for: ')


if __name__ == "__main__":
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
                detik_scrape(keyword, page_number, folder)
            case "2":
                pikiran_rakyat_scrape(keyword, page_number, folder)
            case "3":
                cnn_indonesia_scrape(keyword, page_number, folder)
            case "4":
                tribunnews_scrape(keyword, page_number, folder)
            case "5":
                kompas_scrape(keyword, page_number, folder)
            case _:
                print('Please input the correct menu')

        if len(sys.argv) > 1:
            menu = '0'
