import math, datetime, calendar
import threading, winsound
import pyautogui as gui
from prettytable import PrettyTable

from CustomModules.VariablesModule import *
from CustomModules.EstablishConnection import *

Today = datetime.date.today()
Month = calendar.month_name[Today.month].upper()
PreviousMonth = calendar.month_name[Today.month-1].upper()
Year = Today.strftime(r'%Y')


def InsertData_WaterPurchaseDetails():
    Date, _ = GetDate()

    while True:
        TotalExpense = input('\nTotal Water Purchase Expense: ')
        if TotalExpense.isdigit():
            TotalExpense = int(TotalExpense)
            break
        else:
            print('INVALID Date, TRY AGAIN...')

    print()
    cursor.execute("INSERT INTO [Water Purchase Details] VALUES (?, ?, ?);", (Date, TotalExpense, Month))
    cursor.commit()

def InsertData_UnusualDepartureDetails():
    Date, DateOBJ = GetDate('Enter The Departure Date: ')

    # ROOM/SHOP ID & TENANT VACATING
    while True:
        ID = GetDetails('Room/Shop ID', PossibleValues=list(Shop_IDs + Room_IDs))

        cursor.execute(f"SELECT [Tenant ID], [Tenant Name], [Room/Shop ID] FROM [Occupancy Information] \
                         WHERE [Room/Shop ID] = '{ID}' AND [To (Date)] IS NULL")
        Records = cursor.fetchall()
        if len(Records) == 0:
            print('\n', '-' * 50, sep='')
            print(f'No Tenant Occupying This Room/Shop (ID: {ID}), TRY AGAIN...')
            print('-' * 50, '\n', sep='')
            winsound.Beep(1000, 500)
            continue

        TenantCount = len(Records)
        Table = PrettyTable()
        Table.field_names = ['Tenant ID', 'Tenant Name', 'Room/Shop ID']
        Table.align['Tenant Name'] = 'l'
        Table.add_rows(Records)
        print('\n', Table, sep='', end='\n\n')

        if GetUser_Confirmation('>> Is This The Correct MATCH?'):
            break

    DaysOccupied = GetDetails('Number Of Days Occupied', int, PossibleValues=list(range(31)))
    ClosingReading = round(GetDetails(f"'Closing Sub-Meter Reading' For The Room/Shop (ID: {ID})", float), 1)

    # OPENING READING
    cursor.execute(f"SELECT [Closing Sub-Meter Reading], [Closing Date] FROM [Unusual Occupancy Details] WHERE [For The Month Of] = '{Month}'\
                     AND [Year (YYYY)] = '{Year}' AND [Room/Shop ID] = '{ID}';")
    UODRecords = cursor.fetchall()
    if len(UODRecords) == 0:
        cursor.execute(f"SELECT [Closing Sub-Meter Reading] FROM [Monthly Report Data] WHERE [For The Month Of] = '{PreviousMonth}' \
                         AND [Year (YYYY)] = '{Year}' AND [Room/Shop ID] = '{ID}';")
        OpeningReading, = cursor.fetchone()
    else:
        DateOBJs = [datetime.datetime.strptime(str(Record[1])[:10], r'%Y-%m-%d') for Record in UODRecords]
        MaxDate = max(DateOBJs)
        OpeningReading, = (Record[0] for Record in UODRecords if MaxDate == datetime.datetime.strptime(str(Record[1])[:10], r'%Y-%m-%d'))
    OpeningReading = round(OpeningReading, 1)

    Table = PrettyTable()
    Table.field_names = ['Room/Shop ID', 'Number Of Days Occupied', 'Closing Sub-Meter Reading', 'Opening Sub-Meter Reading', 'Closing Date', 'For The Month Of']
    Table.add_row([ID, DaysOccupied, ClosingReading, OpeningReading, datetime.date.strftime(DateOBJ, r'%d-%m-%Y'), Month])
    print('\n', Table, sep='')
    print()

    # VERIFICATION
    if GetUser_Confirmation('Do You Want To Edit This Record?', ['Y'], ['N', '']):
        print()
        return InsertData_UnusualDepartureDetails()

    cursor.execute(f"SELECT * FROM [Room/Shop Data] WHERE [Room/Shop ID] = '{ID}';")
    Record = cursor.fetchone()
    RoomRent, OtherCharges, CurrentCharge = Record[TenantCount], Record[TenantCount+3], Record[8]

    TotalRent = math.ceil((RoomRent + OtherCharges) * DaysOccupied / 30) + math.ceil((ClosingReading - OpeningReading)*float(CurrentCharge))

    cursor.execute("INSERT INTO [Unusual Occupancy Details] VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", (ID, DaysOccupied, TenantCount, ClosingReading, OpeningReading, Date, Month, TotalRent, Year))
    cursor.commit()
    print()
    return ID, Date

def InsertData_PaymentDetailsNS(ID = None, Date = None, IsDeparture = True):
    def GetReceiptNumber(Table):
        cursor.execute(f"SELECT MAX([Receipt Number]) FROM [{Table}] WHERE [Year (YYYY)] = '{Year}';")
        RawData, = cursor.fetchone()
        return int(RawData) if RawData is not None else 0

    ReceiptNumber = max(GetReceiptNumber('Payment Details'), GetReceiptNumber('Payment Details (NS)')) + 1
    ID = GetDetails('Room/Shop ID', CanBeNONE=None, PossibleValues= list(Shop_IDs + Room_IDs)) if ID is None else ID

    cursor.execute(f"SELECT [Tenant ID], [Tenant Name] FROM [Occupancy Information] WHERE [Room/Shop ID] = '{ID}' AND [To (Date)] IS NULL;")
    OIRecords = cursor.fetchall()
    if IsDeparture:
        TenantIDs = [str(Record[0]) for Record in OIRecords]
        Table = PrettyTable()
        Table.field_names = ['Tenant ID', 'Tenant Name']
        Table.align['Tenant Name'] = 'l'
        Table.add_rows(OIRecords)
        print('\n', Table, sep='')

        print("\n\n----ENTER '' IF EVERYONE | 'NONE' IF NO ONE IS VACATING----")
        while True:
            RawData = input('Enter The Vacating Tenant ID(s) (eg. 0033, 0044): ').strip()
            if RawData in ['', 'NONE']:
                VacatingTenant_List = TenantIDs if RawData == '' else []
                break
            else:
                IsRunning, VacatingTenant_List = GenerateList('Vacating Tenant ID(s) (eg. 0033, 0044)', RawData)
                if not IsRunning:
                    if all(TenantID.isdigit() for TenantID in VacatingTenant_List):
                        VacatingTenant_List = ["{:04d}".format(int(TenantID)) for TenantID in VacatingTenant_List]
                        if all(TenantID in TenantIDs for TenantID in VacatingTenant_List):
                            break
                print('>> INVALID Tenant ID, TRY AGAIN <<')
                winsound.Beep(1000, 500)

    print()
    ReceiptNumber_List = []
    if OIRecords != []:
        TenantCount = len(OIRecords)

        cursor.execute(f"SELECT [Total Rent], [Closing Date] FROM [Unusual Occupancy Details] WHERE [Room/Shop ID] = '{ID}' \
                         AND [For The Month Of] = '{Month}'")
        RawRecords = cursor.fetchall()
        if len(RawRecords) == 0:
            print('\n', '-' * 75, sep='')
            print(">> No Record FOUND, TRY UPDATING 'Unusual Occupancy Details' Table <<")
            print('-' * 75, '\n', sep='')
            winsound.Beep(1000, 500)
            return
        else:
            DateOBJs = [datetime.datetime.strptime(str(Record[1])[:10], r'%Y-%m-%d') for Record in RawRecords]
            MaxDate = max(DateOBJs)
            TotalRent, = (Record[0] for Record in RawRecords if MaxDate == datetime.datetime.strptime(str(Record[1])[:10], r'%Y-%m-%d'))

        for OIRecord in OIRecords:
            ReceiptNumber_List.append(ReceiptNumber)
            TenantID, TenantName = OIRecord

            if TenantID in VacatingTenant_List:
                cursor.execute(f"SELECT [DUE Amount] FROM [DUE Details] WHERE [Tenant ID] = '{TenantID}' AND [For The Month Of] = '{PreviousMonth}';")
                RawData = cursor.fetchone()
                BalanceDue = int(RawData[0]) if RawData != None else 0

                TotalTenantCount = 0
                cursor.execute("SELECT * FROM [Occupancy Information] WHERE [To (Date)] IS NULL;")
                Records = cursor.fetchall()
                for Record in Records:
                    TotalTenantCount += 1 if Record[0] in Room_IDs else 0

                cursor.execute(f"SELECT SUM([Amount]) FROM [Water Purchase Details] WHERE [For The Month Of] = '{Month}'")
                Data = cursor.fetchone()
                TotalWaterCharge = math.ceil(Data[0]) if Data[0] != None else 0

                IndividualRent = math.ceil(TotalRent / TenantCount) + BalanceDue + math.ceil(TotalWaterCharge / TotalTenantCount)
                Date = Today if Date is None else Date
                cursor.execute(f"INSERT INTO [Payment Details (NS)] VALUES ({ReceiptNumber}, '{TenantID}', '{TenantName}', '{ID}', {IndividualRent}, 'PAID', ?, '{Month}', '{Year}');", (Date,))
                cursor.commit()
            else:
                IndividualRent = math.ceil(TotalRent / TenantCount)
                cursor.execute(f"INSERT INTO [Payment Details (NS)] VALUES ({ReceiptNumber}, '{TenantID}', '{TenantName}', '{ID}', {IndividualRent}, 'UNPAID', NULL, '{Month}', '{Year}');")
                cursor.commit()

            ReceiptNumber += 1
    return Month, ReceiptNumber_List, VacatingTenant_List

def InsertData_TenantsInformation():
    RegistrationDate, DateOBJ = GetDate('Registration Date')

    cursor.execute("SELECT MAX(ID) FROM [Tenant's Information]")
    ID = "{:04d}".format(int(cursor.fetchone()[0])+1)

    Fields = {
        'Full Name': (str, 'UPPER'), 
        "Father's Name": (str, 'UPPER'), 
        'Occupation': (str, 'UPPER'), 
        'Permanent Address': (str, 'CAPITALIZE'), 
        'PIN Code': (str,), 
        'Phone Number': (str,), 
        'Additional Phone Number': (str,), 
        'Office Address': (str, 'CAPITALIZE'), 
        'Advance Amount': (int,), 
        'Receipt Number': (int,)
    }
    DataMappings = {'ID': ID}
    print('\n\n<<<<<<<<<<+>>>>>>>>>>')
    for Key, Value in Fields.items():
        if len(Value) == 1:
            DataMappings[Key] = GetDetails(Key, Value[0])
        elif len(Value) == 2:
            DataMappings[Key] = GetDetails(Key, Value[0], StringType=Value[1])
    print('\n<<<<<<<<<<+>>>>>>>>>>\n')

    print('\n<<<<<<<<<<+>>>>>>>>>>', end='')
    StartingIndex = 1
    while True:
        for Index, (Key, Value) in enumerate(list(DataMappings.items())[StartingIndex:]):
            Table = PrettyTable()
            Table.field_names = [Key]
            Table.add_row([Value])
            print('\n\n', Table, sep='')
            if GetUser_Confirmation('Do You Want To Edit This Data?', ['Y'], ['N', '']):
                DataMappings[Key] = GetDetails(Key, type(Value), Value, StringType=Fields[Key][1])
                StartingIndex += Index
                break
        else:
            break
    print('\n<<<<<<<<<<+>>>>>>>>>>\n')

    cursor.execute("""
                   INSERT INTO [Tenant's Information] (
                       [ID], [Full Name], [Father's Name], [Occupation], [Permanent Address], [PIN Code], [Phone Number],
                       [Additional Phone Number], [Office Address], [Advance Amount], [Receipt Number], [Current Status],
                       [Registration Date]
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", tuple(DataMappings.values()) + ('OCCUPIED', RegistrationDate))
    cursor.commit()
    return ID, DateOBJ

def InsertData_OccupancyInformation(TenantID = None, Date = None, TimeDelta = None):
    print('\n\n<<<<<<<+>>>>>>>')
    Date, DateOBJ = GetDate("Desired 'From (Date)'", Date)
    if TimeDelta is not None:
        DateOBJ += datetime.timedelta(days= TimeDelta)
        Date = DateOBJ.strftime(r'%d/%m/%Y')

    # Tenant ID
    while True:
        TenantID = "{:04d}".format(int(GetDetails('Tenant ID'))) if TenantID is None else TenantID
        cursor.execute(f"SELECT [Full Name] FROM [Tenant's Information] WHERE ID = '{TenantID}';")
        RawData = cursor.fetchone()
        if RawData is not None:
            TenantName = str(RawData[0])
            break
        else:
            TenantID = None
            print('INVALID Tenant ID, TRY AGAIN...')

    ID = GetDetails(f'Occupying Room/Shop ID (ID: {TenantID}; Name: {TenantName})', PossibleValues= list(Shop_IDs + Room_IDs))
    ShopName = GetDetails('Shop Name', CanBeNONE=True) if ID in Room_IDs else None
    print('\n<<<<<<<+>>>>>>>\n')

    Table = PrettyTable()
    Table.field_names = ['Room/Shop ID', 'Tenant ID', 'Tenant Name', 'Shop Name', 'From (Date)']
    Table.add_row([ID, TenantID, TenantName, ShopName, DateOBJ.strftime(r'%d-%m-%Y')])
    print('\n', Table, sep='')

    # VERIFICATION
    if GetUser_Confirmation('Do You Want To Edit This Record?', ['Y'], ['N', '']):
        print()
        return InsertData_OccupancyInformation()

    cursor.execute("INSERT INTO [Occupancy Information] VALUES (?, ?, ?, ?, ?, ?);", (ID, TenantID, TenantName, ShopName, Date, None))
    cursor.commit()
    print()
    return TenantID



RawData = None
def GetDetails(WhatToGet: str, DataType = str, DefaultValue = '', CanBeNONE = False, PossibleValues = [], StringType = None):
    def GetInput():
        global RawData
        RawData = input(f'\nEnter The {WhatToGet}: ').strip()
    def InsertValue():
        gui.typewrite(DefaultValue)

    while True:
        GetInput_Thread = threading.Thread(target=GetInput)
        InsertValue_Thread = threading.Thread(target=InsertValue)
        GetInput_Thread.start()
        InsertValue_Thread.start()
        GetInput_Thread.join()
        if RawData != '':
            try:
                ConvertedData = DataType(RawData)
                if StringType == 'UPPER':
                    ConvertedData = ConvertedData.upper()
                elif StringType == 'CAPITALIZE':
                    ConvertedData = ' '.join([Word.capitalize() if Word.replace(',', '').isalpha() and not Word.isupper() else Word for Word in ConvertedData.split()])

                if not PossibleValues or ConvertedData in PossibleValues: 
                    return ConvertedData
                else:
                    print(f'INVALID {WhatToGet}, TRY AGAIN...')
            except ValueError:
                print(f'INVALID {WhatToGet}, TRY AGAIN...')
        elif CanBeNONE is None:
            print(f'INVALID {WhatToGet}, TRY AGAIN...')
        elif CanBeNONE:
            return None
        else:
            return 'NONE' if DataType == str else None

def GetDate(IString, DateOBJ: datetime.date = None):
    while True:
        Date = input(f"\nEnter The {IString} (DD/MM/YYYY): ").strip()
        if Date == '':
            Date = Today.strftime(r'%Y-%m-%d') if DateOBJ is None else DateOBJ.strftime(r'%Y-%m-%d')
            return Date, DateOBJ
        else:
            try:
                DateOBJ = datetime.datetime.strptime(Date, r'%d/%m/%Y')
                Date = datetime.date.strftime(DateOBJ, r'%Y-%m-%d')
                return Date, DateOBJ
            except Exception:            
                print('INVALID Date, TRY AGAIN...')

def GetUser_Confirmation(QString, YES = ['Y', ''], NO = ['N']):
    while True:
        ANS = input('\n' + QString + ' (Y/N): ').strip().upper()
        if ANS in YES:
            return True
        elif ANS in NO:
            return False
        else:
            print('>> INVALID Response, TRY AGAIN <<')

def GenerateList(WhatToGet, Elements = None):
    Elements = input(f'\nEnter The {WhatToGet}: ').upper() if Elements is None else Elements
    a = Elements.split(',')
    for i in range(len(a)):
        a[i] = a[i].strip()

    List = []
    for i in a:
        if '-' in i:
            Start, End = i.split('-')
            Start, End = Start.strip(), End.strip()

            if Start.isdigit() and End.isdigit():
                Start, End = int(Start), int(End)
            else:
                print(f'INVALID {WhatToGet}, TRY AGAIN...')
                return True, None

            List.extend([str(ID) for ID in range(Start, End+1)])
        else:
            List.append(i)
    return False, List

