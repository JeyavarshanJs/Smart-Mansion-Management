import math, datetime, calendar
import threading
import pyautogui as gui
from prettytable import PrettyTable

from CustomModules.VariablesModule import *
from CustomModules.EstablishConnection import *

Today = datetime.date.today()


def InsertData_WaterPurchaseDetails():
    _, _, Month, _ = GetMonth()

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
    _, PreviousMonth, Month, _ = GetMonth()

    Date, DateOBJ = GetDate()

    # ROOM/SHOP ID & TENANT VACATING
    IsRunning = True
    while IsRunning:
        ID = GetDetails('Room/Shop ID', PossibleValues=list(Shop_IDs + Room_IDs))

        cursor.execute(f"SELECT [Tenant ID], [Tenant Name], [Room/Shop ID] FROM [Occupancy Information] WHERE [Room/Shop ID] = '{ID}' AND [To (Date)] IS NULL")
        Records = cursor.fetchall()

        Table = PrettyTable()
        Table.field_names = ['Tenant ID', 'Tenant Name', 'Room/Shop ID']
        Table.align['Tenant Name'] = 'l'
        Table.add_rows(Records)
        print('\n', Table, sep='', end='\n\n')

        if GetUser_Confirmation('>> Is This The Correct MATCH?'):
            break

    DaysOccupied = GetDetails('Number Of Days Occupied', int, '', PossibleValues=list(range(31)))

    ClosingReading = round(GetDetails(f"'Closing Sub-Meter Reading' For The Room/Shop (ID: {ID})", float), 1)

    # OPENING READING
    cursor.execute(f"SELECT [Closing Sub-Meter Reading], [Closing Date] FROM [Unusual Occupancy Details] WHERE [For The Month Of] = '{Month}' AND [Room/Shop ID] = '{ID}';")
    RawRecords = cursor.fetchall()
    if len(RawRecords) == 0:
        cursor.execute(f"SELECT [Closing Sub-Meter Reading] FROM [Monthly Report Data] WHERE [For The Month Of] = '{PreviousMonth}' AND [Room/Shop ID] = '{ID}';")
        OpeningReading = cursor.fetchone()[0]
    else:
        DateOBJs = [datetime.datetime.strptime(str(Record[1])[:10], r'%Y-%m-%d') for Record in RawRecords]
        MaxDate = max(DateOBJs)

        OpeningReading = None
        for Record in RawRecords:
            OpeningReading = Record[0] if MaxDate == datetime.datetime.strptime(str(Record[1])[:10], r'%Y-%m-%d') else OpeningReading
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

    print()
    cursor.execute(f"SELECT * FROM [Room/Shop Data] WHERE [Room/Shop ID] = '{ID}';")
    Record = cursor.fetchone()
    ID = Record[0]
    cursor.execute(f"SELECT COUNT(*) FROM [Occupancy Information] WHERE [Room/Shop ID] = '{ID}' AND [To (Date)] IS NULL;")
    TenantCount = cursor.fetchone()[0]

    Room_Rent = Record[TenantCount+1] if TenantCount != 0 else 0
    Other_Charges = Record[TenantCount+4] if TenantCount != 0 else 0
    Current_Charge = Record[8]

    TotalRent = math.ceil((Room_Rent + Other_Charges) * DaysOccupied / 30) + math.ceil((ClosingReading - OpeningReading)*float(Current_Charge)) if TenantCount != 0 else 0

    cursor.execute("INSERT INTO [Unusual Occupancy Details] VALUES (?, ?, ?, ?, ?, ?, ?);", (ID, DaysOccupied, ClosingReading, OpeningReading, Date, Month, TotalRent))
    cursor.commit()
    return ID, Date

def InsertData_PaymentDetailsNS(ID = None, Date = None, IsDeparture = True):
    _, PreviousMonth, Month, Year = GetMonth()

    cursor.execute("SELECT MAX([Receipt Number]) FROM [Payment Details]")
    RawReceiptNumber_S = cursor.fetchone()
    ReceiptNumber_S = int(RawReceiptNumber_S[0]) if RawReceiptNumber_S[0] != None else 0

    cursor.execute("SELECT MAX([Receipt Number]) FROM [Payment Details (NS)]")
    RawReceiptNumber_NS = cursor.fetchone()
    ReceiptNumber_NS = int(RawReceiptNumber_NS[0]) if RawReceiptNumber_NS[0] != None else 0

    ReceiptNumber = max(ReceiptNumber_S, ReceiptNumber_NS) + 1

    # ROOM/SHOP ID
    if ID == None:
        while True:
            ID = input('\nEnter Room/Shop ID: ').strip().upper()
            if ID in list(Shop_IDs + Room_IDs):
                break
            else:
                print('INVALID Room/Shop ID, TRY AGAIN...')

    VacatingTenant_List = []
    if IsDeparture:
        cursor.execute(f"SELECT [Tenant ID] FROM [Occupancy Information] WHERE [Room/Shop ID] = '{ID}'")
        Records = cursor.fetchall()
        TenantIDs = [Record[0] for Record in Records]
        while True:
            print("\n\n----ENTER '' IF EVERYONE | 'NONE' IF NO ONE IS VACATING----")
            RawData = input('Enter The Vacating Tenant ID(s) (eg. 0033, 0044): ').strip()
            if RawData == '':
                VacatingTenant_List = TenantIDs
                break
            elif RawData == 'NONE':
                break
            else:
                x = RawData.split(',')
                for TenantID in x:
                    TenantID = TenantID.strip()
                    if TenantID.isdigit():
                        TenantID = "{:04d}".format(int(TenantID))
                        if TenantID in TenantIDs:
                            VacatingTenant_List.append(TenantID)
                        else:
                            print('INVALID TenantID, TRY AGAIN...')
                            break
                    else:
                        print('INVALID TenantID, TRY AGAIN...')
                        break
                else:
                    break

    print()
    cursor.execute(f"SELECT [Tenant ID], [Tenant Name] FROM [Occupancy Information] WHERE [Room/Shop ID] = '{ID}' AND [To (Date)] IS NULL;")
    OIRecords = cursor.fetchall()
    ReceiptNumber_List = []
    
    if OIRecords != []:
        TenantCount = len(OIRecords)

        cursor.execute(f"SELECT [Total Rent], [Closing Date] FROM [Unusual Occupancy Details] WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}'")
        RawRecords = cursor.fetchall()
        if len(RawRecords) == 0:
            print('\n', '-' * 75, sep='')
            print("No Record FOUND, TRY UPDATING 'Unusual Occupancy Details' Field...")
            print('-' * 75, '\n', sep='')
            return
        else:
            DateOBJs = [datetime.datetime.strptime(str(Record[1])[:10], r'%Y-%m-%d') for Record in RawRecords]
            MaxDate = max(DateOBJs)

            TotalRent = None
            for Record in RawRecords:
                TotalRent = Record[0] if MaxDate == datetime.datetime.strptime(str(Record[1])[:10], r'%Y-%m-%d') else TotalRent

        for OIRecord in OIRecords:
            ReceiptNumber_List.append(ReceiptNumber)
            TenantID = OIRecord[0]
            TenantName = OIRecord[1]

            cursor.execute(f"SELECT [DUE Amount] FROM [DUE Details] WHERE [Tenant ID] = '{TenantID}' AND [For The Month Of] = '{PreviousMonth}';")
            RawData = cursor.fetchone()
            BalanceDue = int(RawData[0]) if RawData != None else 0

            # TOTAL TENANT COUNT
            TotalTenantCount = 0
            cursor.execute(f"SELECT * FROM [Occupancy Information] WHERE [To (Date)] IS NULL;")
            Records = cursor.fetchall()
            for Record in Records:
                TotalTenantCount += 1 if Record[0] in Room_IDs else 0

            cursor.execute(f"SELECT SUM([Amount]) FROM [Water Purchase Details] WHERE [For The Month Of] = '{Month}'")
            Data = cursor.fetchone()
            TotalWaterCharge = math.ceil(Data[0]) if Data[0] != None else 0

            if TenantID in VacatingTenant_List:
                IndividualRent = math.ceil(TotalRent / TenantCount) + BalanceDue + math.ceil(TotalWaterCharge / TotalTenantCount)
                Date = Today if Date == None else Date
                cursor.execute(f"INSERT INTO [Payment Details (NS)] VALUES ({ReceiptNumber}, '{TenantID}', '{TenantName}', '{ID}', {IndividualRent}, 'PAID', ?, '{Month}', '{Year}');", (Date,))
                cursor.commit()
            else:
                IndividualRent = math.ceil(TotalRent / TenantCount)
                cursor.execute(f"INSERT INTO [Payment Details (NS)] VALUES ({ReceiptNumber}, '{TenantID}', '{TenantName}', '{ID}', {IndividualRent}, 'UNPAID', NULL, '{Month}', '{Year}');")
                cursor.commit()

            ReceiptNumber += 1
    return Month, ReceiptNumber_List, VacatingTenant_List

def InsertData_TenantsInformation():
    RegistrationDate, _ = GetDate()

    cursor.execute("SELECT MAX(ID) FROM [Tenant's Information]")
    ID = "{:04d}".format(int(cursor.fetchone()[0])+1)

    Fields = ['ID', 'Full Name', "Father's Name", 'Occupation', 'Permanent Address', 'PIN Code', 'Phone Number', 'Additional Phone Number', 'Office Address',
              ('Advance Amount', int), ('Receipt Number', int)]
    DataMappings = {'ID': ID}
    print('\n\n<<<<<<<<<<+>>>>>>>>>>')
    for Field in Fields[1:]:
        if isinstance(Field, str):
            DataMappings[Field] = GetDetails(Field)
        elif isinstance(Field, tuple):
            DataMappings[Field[0]] = GetDetails(Field[0], Field[1])
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
                DataMappings[Key] = GetDetails(Key, type(Value), Value)
                StartingIndex += Index
                break
        else:
            break
    print('\n<<<<<<<<<<+>>>>>>>>>>\n')

    cursor.execute("INSERT INTO [Tenant's Information] (ID, [Full Name], [Father's Name], Occupation, [Permanent Address], [PIN Code], [Phone Number], [Additional Phone Number], [Office Address], [Advance Amount], [Receipt Number], [Current Status], [Registration Date]) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", \
        (DataMappings['ID'], DataMappings['Full Name'], DataMappings["Father's Name"], DataMappings['Occupation'], DataMappings['Permanent Address'],
         DataMappings['PIN Code'], DataMappings['Phone Number'], DataMappings['Additional Phone Number'], DataMappings['Office Address'], DataMappings['Advance Amount'],
         DataMappings['Receipt Number'], 'OCCUPIED', RegistrationDate))
    cursor.commit()
    return ID

def InsertData_OccupancyInformation(TenantID = None):
    print('\n\n<<<<<<<<<<+>>>>>>>>>>')
    Date, DateOBJ = GetDate()

    ID = GetDetails('Room/Shop ID', PossibleValues= list(Shop_IDs + Room_IDs))
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
    ShopName = GetDetails('Shop Name', CanBeNONE=True) if ID in Room_IDs else None
    print('\n<<<<<<<<<<+>>>>>>>>>>\n')

    Table = PrettyTable()
    Table.field_names = ['Room/Shop ID', 'Tenant ID', 'Tenant Name', 'Shop Name', 'From (Date)']
    Table.add_row([ID, TenantID, TenantName, ShopName, DateOBJ.strftime(r'%d-%m-%Y')])
    print('\n', Table, sep='')

    # VERIFICATION
    if GetUser_Confirmation('Do You Want To Edit This Record?', ['Y'], ['N', '']):
        print()
        return InsertData_OccupancyInformation()

    cursor.execute(f"INSERT INTO [Occupancy Information] VALUES (?,?,?,?,?,?);", (ID, TenantID, TenantName, ShopName, Date, None))
    cursor.commit()
    print()



RawData = None
def GetDetails(WhatToGet: str, DataType = str, DefaultValue = '', CanBeNONE = False, PossibleValues = []):
    def GetInput():
        global RawData
        RawData = input(f'\nEnter The {WhatToGet}: ')
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
                if PossibleValues != [] and ConvertedData in PossibleValues: 
                    return ConvertedData
                elif PossibleValues == []:
                    return ConvertedData
                else:
                    print(f'INVALID {WhatToGet}, TRY AGAIN...')
            except ValueError:
                print(f'INVALID {WhatToGet}, TRY AGAIN...')
        else:
            if CanBeNONE:
                return None
            else:
                return 'NONE' if DataType == str else None

def GetMonth():
    Month = calendar.month_name[Today.month].upper()
    PreviousMonth = list(MonthNames.values())[(list(MonthNames.values()).index(Month))-1]
    Year = Today.strftime(r'%Y')
    Date = datetime.date.strftime(Today, r'%Y-%m-%d')

    return Date, PreviousMonth, Month, Year

def GetDate():
    while True:
        Date = input("\nEnter The Desired 'From (Date)' (DD/MM/YYYY): ").strip()
        Date = Today.strftime(r'%d/%m/%Y') if Date == '' else Date

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
