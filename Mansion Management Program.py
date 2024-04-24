import time
import os, sys

from CustomModules.EstablishConnection import *
from CustomModules.VariablesModule import ChosenDrive, ChosenPrinter
from CustomModules.MenuMappingsModule import *


def DISPLAY_MENU(MENU_MAPPINGS: dict, MenuTitle):
    print(f'\n<<<+ {MenuTitle} +>>>')
    for ID, Choice in MENU_MAPPINGS.items():
        print(f'{ID})', Choice[0])

    while True:
        User_Choice = input('Enter Your Choice ID: ')   
        if User_Choice in MENU_MAPPINGS:
            return User_Choice
        else:
            print('ID Not Defined, TRY AGAIN...')

def ExecuteAction(MENU_MAPPINGS, MENU_TITLE):
    x = f'SUB MENU ({MENU_TITLE})' if MENU_TITLE != 'MAIN MENU' else 'MAIN MENU'
    User_Choice = DISPLAY_MENU(MENU_MAPPINGS, x)
    Label, Action = MENU_MAPPINGS[User_Choice]

    if User_Choice == '1':
        return Action()

    elif isinstance(Action, dict):
        SUB_MENU_MAPPINGS = Action
        y = f'{MENU_TITLE}_{Label.replace(' ', '_')}' if MENU_TITLE != 'MAIN MENU' else Label.replace(' ', '_')
        Data = ExecuteAction(SUB_MENU_MAPPINGS, y)
        if Data == 'BACK':
            Data = ExecuteAction(MENU_MAPPINGS, MENU_TITLE)
            return Data

    else:
        Action()
        input('\nPress ENTER Key To Continue...')


# Checking Basic Requirements
Required_Files = [r'Static Templates\Room Rent Receipt-1.jpg', r'Static Templates\Room Rent Receipt-2.jpg',
                  r'Static Templates\Shop Rent Receipt-1.jpg', r'Static Templates\Shop Rent Receipt-2.jpg',
                  'CalibriFont Bold.ttf', 'CalibriFont Regular.ttf', 'Data.txt']
os.makedirs('Final Print', exist_ok=True)
os.makedirs('Rent Receipts', exist_ok=True)
if not all(os.path.exists(File) for File in Required_Files):
    print('\n', '-' * 80, sep='')
    print('Requirements NOT SATISFIED!! Some Files May Be Missing, TRY AGAIN...')
    print('-' * 80, '\n', sep='')
    time.sleep(3)
    sys.exit()  

while True:
    os.system('cls')
    print('\n')
    print(' ' * 60 , r'\\!//', sep='')
    print(' ' * 60 , '(o o)', sep='')
    print('-' * 56 , 'oOOo-(_)-oOOo', '-' * 56, sep='')
    print(' ' * 42 , 'GREETINGS From Jeyavarshan, The CREATOR')
    print(' ' * 3, 'For BUG REPORTS & ANY DOUBTS Contact Me VIA (WhatsApp: 8667224050, Phone: 8667224050, Email: jeyavarshan0000@gmail.com)',sep='')
    print('=' * 125)
    print('\n')
    ChosenDrive = ChosenPrinter = None
    Data = ExecuteAction(MENU_MAPPINGS, 'MAIN MENU')
    if Data == 'QUIT':
        print('\n', '-' * 50, sep='')
        print('User TRIGGERED Exit Command...')
        print('-' * 50, '\n', sep='')
        time.sleep(1)
        os.system('cls')
        break


# Close cursor and connection
cursor.close()
con.close()
