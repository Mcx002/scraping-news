from src.services.detik import scrap as detik_scrap


def prompt_menu():
    print('Menu:')
    print('1. Scrap Detik')

    return input('Choose which media you wanna scrap for: ')


def main():
    menu = prompt_menu()

    match menu:
        case "1":
            detik_scrap()
        case _:
            print('Please input the menu')


main()
