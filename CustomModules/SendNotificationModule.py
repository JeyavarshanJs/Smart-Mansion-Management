import pyautogui as gui
import pyperclip
import datetime, calendar, time

from CustomModules.EstablishConnection import *

Today = datetime.date.today()


def ReadData(Delimiter = ':'):
    Data = {}
    with open('Data.txt', 'r') as File:
        for Line in File:
            parts = Line.strip().split(Delimiter)
            if len(parts) == 2:
                key, value = parts
                key = key.strip()
                value = eval(value.strip())
                Data[key] = value
    return Data

def UpdateData(WhatToUpdate, Values: dict, Delimiter = ':'):
    Data = ReadData()

    for Element in WhatToUpdate:
        if Values.get(Element) is None:
            while True:
                Value = input(f'\nEnter {WhatToUpdate}: ')
                if isinstance(Value, type(Data[Element])):
                    Data[Element] = Value
                    break
                else:
                    print('>> INVALID Value, TRY AGAIN...')
        else:
            Data[Element] = Values[Element]

    with open('Data.txt', 'w') as File:
        File.writelines([f'{Key}{Delimiter} {Value}' for Key, Value in Data.items()])


def SendNotification_ALL():
    Month = calendar.month_name[Today.month-1].upper()
    PreviousMonth = calendar.month_name[Today.month-2].upper()

    print('\n<<<<<<<<<<+>>>>>>>>>>', end='')
    if not GetUser_Confirmation("Do You Want To Record Cursor's Position?", ['Y'], ['N', '']):
        if GetUser_Confirmation('Is WhatsApp INSTALLED In Your Machine?'):
            try:
                if GetUser_Confirmation('Is WhatsApp ALREADY Opened In Your Machine?'):
                    Open_WhatsApp(0.5)
                else:
                    Open_WhatsApp(10)

                RawData = GetData(Month)
                for Data in RawData:
                    SendWhatsAppMessage_1(Data)

                cursor.execute(f"SELECT [Tenant ID] FROM [DUE Details] WHERE [For The Month Of] = '{PreviousMonth}' AND NOT [Due Amount] = 0;")
                RawData = cursor.fetchall()
                for Data in RawData:
                    SendWhatsAppMessage_2(Data)
            except gui.FailSafeException:
                print('\n', '-' * 50, sep='')
                print('  User ENDED The Process...')
                print('-' * 50, '\n', sep='')
        else:
            print('\n', '-' * 75, sep='')
            print('  INSTALL WhatsApp Desktop APP, Then TRY AGAIN...')
            print('-' * 75, '\n', sep='')
    else:
        gui.alert(title = 'ALERT', text = "After Confirming This Message, Move The Cursor To The Desired Location And WAIT.")
        time.sleep(30)
        X, Y = gui.position()
        gui.alert(title = 'Data Updated', text = 'Cursor Position Recorded Successfully...')
        UpdateData(['Cursor Position'], {'Cursor Position': (X, Y)})
        SendNotification_ALL()

    print('<<<<<<<<<<+>>>>>>>>>>\n')


# OTHER FUNCTIONS
def SendWhatsAppMessage_1(Data):
    PermanentData = ReadData()
    cursor.execute(f"SELECT [Phone Number] FROM [Tenant's Information] WHERE [ID] = '{Data[0]}'")
    RawPhoneNumber = cursor.fetchone()
    PhoneNumber = str(RawPhoneNumber[0]) if RawPhoneNumber not in ['NONE', None] else ''
    if len(PhoneNumber) != 10 or not PhoneNumber.isdigit():
        return

    Month = calendar.month_name[Today.month].upper()
    Date = int(Today.strftime(r'%d'))
    PreviousMonth = calendar.month_name[Today.month-1].upper()

    gui.hotkey('ctrl', 'n')
    time.sleep(1)
    gui.typewrite(PhoneNumber)
    time.sleep(2)
    gui.click(PermanentData['Cursor Position'][0], PermanentData['Cursor Position'][1], duration=0.25)
    time.sleep(1)

    if Date <= 5:
        MSG = '*வாழ்க வளமுடன்*\n\n' \
            f'GREETINGS From Jeyavarshan😎 (Manager) To Mr./Mrs. {Data[1]}\n' \
            f'     This Is To INFORM You That *TOTAL RENT* For The Month Of {PreviousMonth} For Room/Shop (ID: {Data[2]}) Is *Rs: {int(Data[3])}/-*💰💰.\n\n' \
            '*This Is An AUTO-GENERATED Message*\n' \
            'Hence, For Further Queries _CALL 9245459428 / APPROACH K.JEYAGOPAL (OWNER)_\n\n' \
            '*Hope You Will Settle The Rent Payment Within '
        MSG += f'5th OF {Month}*⏳⏳' if Date < 5 else 'TODAY*⏳⏳'
    else:
        MSG = '⚠️⚠️ *DUE Date Exceeded* ⚠️⚠️\n' \
            '*வாழ்க வளமுடன்*\n\n' \
            f'GREETINGS From Jeyavarshan😎 (Manager) To Mr./Mrs. {Data[1]}\n' \
            f'     This Is To INFORM You That *TOTAL RENT* For The Month Of {PreviousMonth} For Room/Shop (ID: {Data[2]}) Is *Rs: {int(Data[3])}/-*💰💰.\n\n' \
            '*This Is An AUTO-GENERATED Message*\n' \
            'Hence, For Further Queries _CALL 9245459428 / APPROACH K.JEYAGOPAL (OWNER)_\n\n' \
            '*Hope You Will Settle The Rent Payment SOON*⌛⌛'

    pyperclip.copy(MSG)
    gui.hotkey('ctrl', 'v')
    time.sleep(2)

    gui.press('enter')
    time.sleep(1)

def SendWhatsAppMessage_2(Data):
    PermanentData = ReadData()
    cursor.execute(f"SELECT [Phone Number] FROM [Tenant's Information] WHERE [ID] = '{Data[0]}'")
    RawPhoneNumber = cursor.fetchone()
    PhoneNumber = str(RawPhoneNumber[0]) if RawPhoneNumber not in ['NONE', None] else ''
    if len(PhoneNumber) != 10 or not PhoneNumber.isdigit():
        print(f"{Data[0]} Skipped")
        return

    gui.hotkey('ctrl', 'n')
    time.sleep(1)
    gui.typewrite(PhoneNumber)
    time.sleep(2)
    gui.click(PermanentData['Cursor Position'][0], PermanentData['Cursor Position'][1], duration=0.25)
    time.sleep(1)

    gui.typewrite('*Including ALL REMAINING DUES*')
    time.sleep(1)
    gui.press('enter')
    time.sleep(1)

def GetUser_Confirmation(QString, YES = ['Y', ''], NO = ['N']):
    while True:
        ANS = input('\n' + QString + ' (Y/N): ').strip().upper()
        if ANS in YES:
            return True
        elif ANS in NO:
            return False
        else:
            print('>> INVALID Response, TRY AGAIN <<')

def Open_WhatsApp(Delay):
    gui.press('win')
    time.sleep(2)
    gui.typewrite('WhatsApp')
    time.sleep(0.5)
    gui.press('enter')
    time.sleep(Delay)

def GetData(Month):
    Query = f"""
        SELECT [Tenant ID], [Tenant Name], [Room/Shop ID], SUM([Individual Rent]), [For The Month OF] FROM
        (
            SELECT [Tenant ID], [Tenant Name], [Room/Shop ID], [Individual Rent], [For The Month OF] FROM [Payment Details] WHERE [Status] = 'UNPAID' 
            AND [For The Month OF] = '{Month}'
            UNION
            SELECT [Tenant ID], [Tenant Name], [Room/Shop ID], [Individual Rent], [For The Month OF] FROM [Payment Details (NS)] WHERE [Status] = 'UNPAID' 
            AND [For The Month OF] = '{Month}'
        )
        GROUP BY [Tenant ID], [Tenant Name], [Room/Shop ID], [For The Month OF];
    """
    cursor.execute(Query)
    return cursor.fetchall()
