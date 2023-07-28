from src.services.detik import scrap as detik_scrap


def prompt_menu():
    print('Menu:')
    print('0. Stop Application')
    print('1. Scrap Detik')

    return input('Choose which media you wanna scrap for: ')


def main():
    menu = '-1'
    while menu != '0':
        menu = prompt_menu()

        match menu:
            case "0":
                print('Application stopped')
            case "1":
                detik_scrap()
            case _:
                print('Please input the correct menu')

main()
