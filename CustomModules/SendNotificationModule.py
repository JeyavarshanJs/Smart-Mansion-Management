import datetime, calendar, time
import pyautogui as gui
import pyperclip

from CustomModules.EstablishConnection import *
from CustomModules.FetchDataModule import *
from CustomModules.DataHandlingModule import *

Today = datetime.date.today()



def SendNotification_ALL():
    Month = calendar.month_name[Today.month-1].upper()
    PreviousMonth = calendar.month_name[Today.month-2].upper()

    print('\n<<<<<<<<<<+>>>>>>>>>>', end='')
    if GetUser_Confirmation('Is WhatsApp INSTALLED In Your Machine?'):
        OTHER = ['CHECK RCP']
        ANS = GetUser_Confirmation("Do You Want To Record Cursor's Position?", ['Y'], ['N', ''], OTHER)
        if ANS == OTHER[0]:
            gui.moveTo(PermanentData['Cursor Position'][0], PermanentData['Cursor Position'][1], duration=0.25)
        elif not ANS:
            try:
                RawRecords = GetRecords(Month)
                if GetUser_Confirmation('Do You Want To Set OFFSET?', ['Y'], ['N', '']):
                    while True:
                        TenantID = input('\n>> Enter The LAST Tenant ID: ').strip().upper()
                        if TenantID == 'FIND TENANT ID':
                            print('\n<<<<+>>>>')
                            Data = FetchData_TenantID_FROM_TenantName(False)
                            print('\n'.join([f"   {i+1}) Name: {TenantName}{' ' * (20 - len(TenantName))} --->  ID: {TenantID}" for i, (TenantID, TenantName) in enumerate(Data)]))
                            print('\n<<<<+>>>>\n')
                        elif TenantID.isdigit():
                            TenantID = "{:04d}".format(int(TenantID))
                            Count = sum(1 for Record in RawRecords if TenantID == str(Record[0]))

                            if Count == 1:
                                Offset, = (Index for Index, Record in enumerate(RawRecords) if str(Record[0]) == TenantID)
                                break
                            elif Count > 1:
                                while True:
                                    ID = input('\n>> More Than One Record FOUND. So Enter LAST Room/Shop ID: ').strip().upper()
                                    if ID in list(Shop_IDs + Room_IDs):
                                        break
                                    print('>> INVALID Room/Shop ID, TRY AGAIN <<')
                                Offset, = (Index for Index, Record in enumerate(RawRecords) if str(Record[0]) == TenantID and str(Record[2]) == ID)
                                break
                            else:
                                print('>> No Record Match With This Tenant ID <<')
                        else:
                            print('>> INVALID Tenant ID, TRY AGAIN <<')
                else:
                    Offset = -1
                IsOpened = True if GetUser_Confirmation('Is WhatsApp ALREADY Opened In Your Machine?', ['Y'], ['N', '']) else False
                Open_WhatsApp()

                for Data in RawRecords[Offset+1:]:
                    SendWhatsAppMessage_1(Data)
                    cursor.execute(f"SELECT [Tenant ID] FROM [DUE Details] WHERE [For The Month Of] = '{PreviousMonth}' AND [Tenant ID] = '{Data[0]}' AND NOT [Due Amount] = 0;")
                    DDRecords = cursor.fetchone()
                    if DDRecords is not None:
                        SendWhatsAppMessage_2(DDRecords[0])

                if IsOpened:
                    gui.hotkey('alt', 'tab')
                else:
                    gui.hotkey('alt', 'f4')
            except gui.FailSafeException:
                print('\n', '-' * 50, sep='')
                print('  The Process Has Been STOPPED By The User...')
                print('-' * 50, '\n', sep='')
        else:
            gui.alert(title = 'ALERT', text = "After Confirming This Message, Move The Cursor To The Desired Location And WAIT.")
            time.sleep(30)
            X, Y = gui.position()
            gui.alert(title = 'Data Updated', text = 'Cursor Position Recorded Successfully...')
            UpdatePermanentData(['Cursor Position'], {'Cursor Position': (X, Y)})
            SendNotification_ALL()
    else:
        print('\n', '-' * 75, sep='')
        print('  INSTALL WhatsApp Desktop APP, Then TRY AGAIN...')
        print('-' * 75, '\n', sep='')

    print('<<<<<<<<<<+>>>>>>>>>>\n')


# OTHER FUNCTIONS
def SendWhatsAppMessage_1(Data):
    cursor.execute(f"SELECT [Phone Number] FROM [Tenant's Information] WHERE [ID] = '{Data[0]}'")
    RawPhoneNumber = cursor.fetchone()
    PhoneNumber = str(RawPhoneNumber[0]) if RawPhoneNumber not in ['NONE', None] else ''
    if len(PhoneNumber) != 10 or not PhoneNumber.isdigit():
        return

    Month = calendar.month_name[Today.month].upper()
    Date = int(Today.strftime(r'%d'))
    PreviousMonth = calendar.month_name[Today.month-1].upper()

    gui.hotkey('ctrl', 'n')
    time.sleep(1.5)
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
    cursor.execute(f"SELECT [Phone Number] FROM [Tenant's Information] WHERE [ID] = '{Data[0]}'")
    RawPhoneNumber = cursor.fetchone()
    PhoneNumber = str(RawPhoneNumber[0]) if RawPhoneNumber not in ['NONE', None] else ''
    if len(PhoneNumber) != 10 or not PhoneNumber.isdigit():
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

def GetUser_Confirmation(QString, YES = ['Y', ''], NO = ['N'], OTHER: list = []):
    while True:
        ANS = input('\n' + QString + ' (Y/N): ').strip().upper()
        if ANS in YES:
            return True
        elif ANS in NO:
            return False
        elif OTHER and ANS in OTHER:
            return ANS
        else:
            print('>> INVALID Response, TRY AGAIN <<')

def Open_WhatsApp():
    print('\n\n', '-' * 125, sep='')
    print('    >> The Notification Sending Process is about to commence in 10 seconds.')
    print('    >> Please ensure that the process is running smoothly.')
    print('    >> If you detect any issues, promptly move your cursor to any corner of the screen to halt the process.')
    print('-' * 125, '\n', sep='')
    time.sleep(10)

    gui.press('win')
    time.sleep(2)
    gui.typewrite('WhatsApp')
    time.sleep(0.5)
    gui.press('enter')
    time.sleep(2)
    gui.confirm("Click 'OK' Button When Your WhatsApp Screen Is Visible & Ready For Sending Messages.", title= 'User Confirmation', buttons= ['OK'])
    time.sleep(1)

def GetRecords(Month):
    Query = f"""
        SELECT [Tenant ID], [Tenant Name], [Room/Shop ID], SUM([Individual Rent]), [For The Month OF] FROM
        (
            SELECT [Tenant ID], [Tenant Name], [Room/Shop ID], [Individual Rent], [For The Month OF] FROM [Payment Details] WHERE [Status] = 'UNPAID' 
            AND [For The Month OF] = '{Month}'
            UNION
            SELECT [Tenant ID], [Tenant Name], [Room/Shop ID], [Individual Rent], [For The Month OF] FROM [Payment Details (NS)] WHERE [Status] = 'UNPAID' 
            AND [For The Month OF] = '{Month}'
        )
        GROUP BY [Tenant ID], [Tenant Name], [Room/Shop ID], [For The Month OF]
        ORDER BY [Tenant ID], [Room/Shop ID];
    """
    cursor.execute(Query)
    return cursor.fetchall()

__all__ = ['SendNotification_ALL']