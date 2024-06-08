import time, winsound
import os, sys

from CustomModules.EstablishConnection import *
from CustomModules.VariablesModule import ChosenDrive, ChosenPrinter
from CustomModules.MenuMappingsModule import *
from CustomModules.DataHandlingModule import *

def DISPLAY_MENU(MENU_MAPPINGS: dict, TITLE: str):
    print(f'\n\n<<<<+ {TITLE} +>>>>\n')
    for ID, Choice in MENU_MAPPINGS.items():
        print(f'{ID})', Choice[0])

    while True:
        User_Choice = input('Enter Your Choice ID: ')   
        if User_Choice in MENU_MAPPINGS:
            return User_Choice
        else:
            print('>> ID Not Defined, TRY AGAIN <<\n')

def ExecuteAction(MENU_MAPPINGS, MENU_TITLE):
    User_Choice = DISPLAY_MENU(MENU_MAPPINGS, f'SUB MENU ({MENU_TITLE})' if MENU_TITLE != 'MAIN MENU' else 'MAIN MENU')
    Label, Action = MENU_MAPPINGS[User_Choice]

    if Label in ['BACK', 'EXIT']:
        return Action()

    elif isinstance(Action, dict):
        os.system('cls')
        SUB_MENU_MAPPINGS = Action
        Data = ExecuteAction(SUB_MENU_MAPPINGS, f'{MENU_TITLE}_{Label.replace(' ', '_')}' if MENU_TITLE != 'MAIN MENU' else Label.replace(' ', '_'))
        if Data == 'BACK':
            os.system('cls')
            Data = ExecuteAction(MENU_MAPPINGS, MENU_TITLE)
            return Data

    else:
        print(f'\n\n\n<<<+ {MENU_TITLE} ({Label}) +>>>')
        Action()
        input('\nPress ENTER Key To Continue...')


# Checking Basic Requirements
Required_Files = [r'Static Templates\Room Rent Receipt-1.jpg', r'Static Templates\Room Rent Receipt-2.jpg',
                  r'Static Templates\Shop Rent Receipt-1.jpg', r'Static Templates\Shop Rent Receipt-2.jpg',
                  r'Fonts\CalibriFont Bold.ttf', r'Fonts\CalibriFont Regular.ttf', 'Data.txt']
if PermanentData['Output Location'] == '':
    UpdatePermanentData(['Output Location'], {'Output Location': f'{os.getcwd()}\\'})

os.makedirs(rf'{PermanentData['Output Location']}Final Print', exist_ok=True)
os.makedirs(rf'{PermanentData['Output Location']}Rent Receipts', exist_ok=True)
if not all(os.path.exists(File) for File in Required_Files):
    print('\n', '-' * 80, sep='')
    print('>> Requirements NOT SATISFIED!! Some Files May Be Missing, TRY AGAIN <<')
    print('-' * 80, '\n', sep='')
    winsound.Beep(1000, 500)
    time.sleep(3)
    sys.exit()  

while True:
    os.system('cls')
    print('\n')
    print(' ' * 60 , r"\\!//", sep='')
    print(' ' * 60 , '(o o)', sep='')
    print('-' * 56 , 'oOOo-(_)-oOOo', '-' * 56, sep='')
    print(' ' * 42 , 'GREETINGS From Jeyavarshan, The CREATOR')
    print(' ' * 3, 'For BUG REPORTS & ANY DOUBTS Contact Me VIA (WhatsApp: 8667224050, Phone: 8667224050, Email: jeyavarshan0000@gmail.com)', sep='')
    print('=' * 125)
    print('\n')
    ChosenDrive = ChosenPrinter = None
    Data = ExecuteAction(MENU_MAPPINGS, 'MAIN MENU')
    if Data == 'EXIT':
        ExitMSG = '😎  THANK YOU For Using My SOFTWARE  😎'
        print('\n\n', ' '* int((125 - 101)/2), '=', '-=' * 50, sep='')
        print(' ' * int((125 - len(ExitMSG))/2), ExitMSG)
        print(' '* int((125 - 101)/2), '=-' * 50, '=', sep='')
        time.sleep(3)
        os.system('cls')
        break


# Close cursor and connection
cursor.close()
con.close()
