import math, datetime, calendar
import winsound
from prettytable import PrettyTable

from CustomModules.VariablesModule import *
from CustomModules.EstablishConnection import *

Today = datetime.date.today()
Year = Today.strftime('%Y') 


def FetchData_TenantName_FROM_TenantID():
    print("\n\n----ENTER 'STOP' TO QUIT----")
    while True:
        TenantID = input('\nEnter The Tenant ID To Fetch Tenant Name: ').strip()
        if TenantID.upper() == 'STOP':
            print()
            break

        if TenantID.isdigit():
            TenantID = "{:04d}".format(int(TenantID))
        else:
            print('INVALID Tenant ID, TRY AGAIN...')
            continue

        cursor.execute(f"SELECT [ID], [Full Name] FROM [Tenant's Information] WHERE ID = '{TenantID}';")
        Record = cursor.fetchone()

        if Record != None:
            print(f"ID: '{Record[0]}'  --->  Name: '{Record[1]}'")
        else:
            print('No Records Found, TRY AGAIN...')

def FetchData_TenantID_FROM_TenantName(IsLoop = True, TenantName = None):
    def FetchData(TenantName):
        if TenantName is None:
            TenantName = input('\nEnter The Tenant Name To Fetch ID: ').strip().upper()
            if TenantName == 'STOP':
                print()
                return 'QUIT'

        cursor.execute(f"SELECT [ID], [Full Name] FROM [Tenant's Information] WHERE [Full Name] LIKE '%{TenantName}%';")
        Records = cursor.fetchall()
        if Records != []:
            return Records
        else:
            print('>> No Records Found, TRY AGAIN <<')

    if IsLoop:
        print("\n\n----ENTER 'STOP' TO QUIT----")
        while True:
            Data = FetchData(TenantName)
            if Data == 'QUIT':
                break
            elif Data is not None:
                print('\n'.join([f"   {i+1}) Name: {TenantName}{' ' * (20 - len(TenantName))} --->  ID: {TenantID}" for i, (TenantID, TenantName) in enumerate(Data)]))
            TenantName = None
    else:
        Data = FetchData(TenantName)
        return Data if Data != 'QUIT' else None

def FetchData_TenantID_FROM_OccupiedSpaceID(IsLoop = True, IString = 'Enter The Room/Shop ID'):
    def FetchData(ID):
        cursor.execute(f"SELECT [Tenant ID], [Tenant Name] FROM [Occupancy Information] WHERE [Room/Shop ID] = '{ID}' AND [To (Date)] IS NULL;")
        Records = cursor.fetchall()

        if Records != []:
            print(f"Tenant(s) Occupying Room/Shop (ID: {ID}) is(are):")
            for i, Record in enumerate(Records):
                print(f'  {i+1}) {Record[1]}  ({Record[0]})')
        else:
            print('No Records Found, TRY AGAIN...')

    if IsLoop:
        print("\n\n----ENTER 'STOP' TO QUIT----")
        while True:
            ID = input('\nEnter The Room/Shop ID: ').strip().upper()
            if ID == 'STOP':
                print()
                break
            elif ID in list(Shop_IDs + Room_IDs):
                FetchData(ID)
            else:
                print('INVALID Tenant ID, TRY AGAIN...')
    else:
        ID = input(f'\n{IString}: ').strip().upper()
        if ID in list(Shop_IDs + Room_IDs):
            FetchData(ID)
        else:
            print('INVALID Room/Shop ID, TRY AGAIN...')

def FetchData_ReceiptNumber_FROM_TenantID(IsLoop = True, TenantID = None, Month = None):
    def FetchData(TenantID):
        if TenantID is None:
            TenantID = input('\nEnter The Tenant ID: ').strip().upper()
            if TenantID in ['STOP', 'CHANGE MONTH'] and IsLoop:
                print()
                return None if TenantID == 'STOP' else FetchData_ReceiptNumber_FROM_TenantID()
            elif TenantID.isdigit():
                TenantID = "{:04d}".format(int(TenantID))
            else:
                print('>> INVALID Tenant ID, TRY AGAIN <<')
                return FetchData(None)

        cursor.execute(f"""
                       SELECT [Receipt Number], [Status] FROM [Payment Details] WHERE [Tenant ID] = '{TenantID}' AND [For The Month Of] = '{Month}'
                       UNION ALL
                       SELECT [Receipt Number], [Status] FROM [Payment Details (NS)] WHERE [Tenant ID] = '{TenantID}' AND [For The Month Of] = '{Month}';
        """)
        Records = cursor.fetchall()

        if Records != []:
            return Records
        elif IsLoop:
            print('>> No Records Found, TRY AGAIN <<')

    if Month is None:
        Month = GetDetails('Desired Month (eg. JAN or JANUARY)', PossibleValues= list(MonthNames.keys()) + list(MonthNames.values()) + [''])
        Month = (
            calendar.month_name[Today.month-1].upper() if Month == '' else 
            MonthNames[Month] if Month in MonthNames.keys() else Month
            )

    if IsLoop:
        print("\n\n----ENTER 'STOP' TO QUIT | 'CHANGE MONTH' TO CHANGE MONTH----")
        while True:
            Data = FetchData(TenantID)
            print(Data)
            TenantID = None
            if Data == 'QUIT':
                break
            elif Data != None:
                print(f"The Receipt Number(s) Correspond To The Tenant (ID: {TenantID}) Is(Are):")
                for i, Record in enumerate(Data):
                    print(f"  {i+1}) {Record[0]}  (Status: {Record[1]})")
    else:
        Data = FetchData(TenantID)
        return Data if Data != 'QUIT' else None

def FetchData_UNPAID_Tenants():
    cursor.execute("""
                SELECT [Tenant ID], [Tenant Name], [Room/Shop ID], [Individual Rent], [For The Month OF] FROM [Payment Details]
                WHERE Status = 'UNPAID' ORDER BY [For The Month Of], [Room/Shop ID]
                UNION ALL
                SELECT [Tenant ID], [Tenant Name], [Room/Shop ID], [Individual Rent], [For The Month OF] FROM [Payment Details (NS)]
                WHERE Status = 'UNPAID' 
                ORDER BY [For The Month Of], [Room/Shop ID], [Tenant ID];
    """)
    RawRecords = cursor.fetchall()

    DetailsTable = PrettyTable()
    DetailsTable.field_names = ['Tenant ID', 'Tenant Name', 'Room/Shop ID', 'Total Amount', 'Phone Number', 'For The Month Of']
    DetailsTable.align['Tenant Name'] = 'l'

    for Record in RawRecords:
        cursor.execute(f"SELECT [Phone Number] FROM [Tenant's Information] WHERE [ID] = '{Record[0]}'")
        PhoneNumber = cursor.fetchone()[0]
        Record = list(Record[:4]) + [PhoneNumber] + list(Record[4:])
        Record[3] = int(Record[3])
        DetailsTable.add_row(Record)
        DetailsTable.add_row(['', '', '', '', '', '']) if Record[0] != RawRecords[-1][0] else None

    print('\n', DetailsTable, sep='')

    SUMTable = PrettyTable()
    SUMTable.field_names = ['Total DUE', 'For The Month Of']
    cursor.execute("""
                SELECT SUM([Individual Rent]), [For The Month Of] FROM
                (
                    SELECT [Individual Rent], [For The Month Of] FROM [Payment Details] WHERE Status = 'UNPAID' 
                    UNION ALL
                    SELECT [Individual Rent], [For The Month Of] FROM [Payment Details (NS)] WHERE Status = 'UNPAID'
                )
                GROUP BY [For The Month Of] ORDER BY SUM([Individual Rent]) DESC;
    """)
    RawRecords = cursor.fetchall()

    for Record in RawRecords:
        Record = list(Record)
        Record[0] = '{:,}'.format(int(Record[0]))
        SUMTable.add_row(Record)

    print('\n', SUMTable, sep='', end='\n\n')

def FetchData_GetTenantDetails():
    def ADD_ROW(Record):
        OccupancyData = RawOccupancyData.pop() if RawOccupancyData != [] else ['', '', '']
        OccupancyData[1] = OccupancyData[1].strftime(r'%d-%m-%Y') if OccupancyData[1] not in ['', None] else ''
        OccupancyData[2] = OccupancyData[2].strftime(r'%d-%m-%Y') if OccupancyData[2] not in ['', None] else ''

        Table.add_row(Record + [''] + list(OccupancyData))

    Fields = ['ID', 'Name', "Father's Name", 'Occupation', 'Permanent Address', 'PIN Code', 'Phone Number-1', 'Phone Number-2', 'Office Address', 'Advance Amount', 'Receipt Number', None, 'Current Status', 'Description', 'Registration Date']
    print("\n\n--- ENTER 'STOP' TO QUIT ---")
    while True:
        TenantID = input('\nEnter Tenant ID To Fetch Details: ').strip().upper()
        if TenantID == 'STOP':
            print()
            break
        elif TenantID == 'FIND TENANT ID':
            print('\n\n<<<<<+>>>>>')
            Data = FetchData_TenantID_FROM_TenantName(False)
            if Data is not None:
                print('\n'.join([f"   {i+1}) Name: {TenantName}{' ' * (20 - len(TenantName))} --->  ID: {TenantID}" for i, (TenantID, TenantName) in enumerate(Data)]))
            print('\n<<<<<+>>>>>\n')
            continue
        elif not TenantID.isdigit():
            print('>> INVALID Tenant ID, TRY AGAIN <<')
            continue

        TenantID = "{:04d}".format(int(TenantID))
        cursor.execute(f"SELECT * FROM [Tenant's Information] WHERE ID = '{TenantID}';")
        Records = cursor.fetchone()
        if Records is None:
            print('\n', '-' * 75, sep='')
            print("No Record FOUND, TRY UPDATING 'Unusual Occupancy Details' Table...")
            print('-' * 75, '\n', sep='')
            winsound.Beep(1000, 500)
            continue

        cursor.execute(f"SELECT [Room/Shop ID], [From (Date)], [To (Date)] FROM [Occupancy Information] WHERE [Tenant ID] = '{TenantID}' ORDER BY [From (Date)];")
        RawOccupancyData = cursor.fetchall()
        Table = PrettyTable()
        Table.field_names = ['KEY', 'VALUE', '', 'Room/Shop ID', 'FROM (Date)', 'TO (Date)']
        Table.align['KEY'] = Table.align['VALUE'] = 'l'
        for Key, Value in zip(Fields, Records):
            if Key is not None:
                Value = int(Value) if Key == 'Advance Amount' else Value
                Value = Value.strftime(r'%d-%m-%Y') if Key == 'Registration Date' else Value
                if Key in ['Permanent Address', 'Office Address', 'Description'] and Value is not None:
                    Value = Value.split()
                    for i in range(math.ceil(len(Value)/4)):
                        ROW = ' '.join(Value[:4])
                        del Value[:4]
                        ADD_ROW([Key, ROW]) if i == 0 else ADD_ROW(['', ROW])
                else:
                    ADD_ROW([Key, Value])

                if Key != Fields[-1]:
                    ADD_ROW(['', ''])

        while RawOccupancyData != []:
            OccupancyData = RawOccupancyData.pop()
            OccupancyData[1] = OccupancyData[1].strftime(r'%d-%m-%Y') if OccupancyData[1] not in ['', None] else ''
            OccupancyData[2] = OccupancyData[2].strftime(r'%d-%m-%Y') if OccupancyData[2] not in ['', None] else ''
            Table.add_row(['', '', ''] + list(OccupancyData))

        print('\n', Table, '\n', sep='')

def FetchDate_Vacancy():
    VacancyCount = 0
    VacantSpace_List = []
    for ID in list(Room_IDs + Shop_IDs):
        cursor.execute(f"SELECT * FROM [Occupancy Information] WHERE [Room/Shop ID] = '{ID}' AND [To (Date)] IS NULL")
        x = cursor.fetchone()
        if x == None:
            VacantSpace_List.append(ID)
            VacancyCount += 1
    print('\nNumber Of Room/Shop Vacant:', VacancyCount)
    print('Vacant Room/Shop(s) is(are): ', end='')
    for ID in VacantSpace_List:
        print(ID, end=', ') if ID != VacantSpace_List[-1] else print(ID)
    print()

def FetchData_TotalCashReceived():
    while True:
        Month = input('\nEnter The Desired Month (eg. JAN or JANUARY): ').strip().upper()
        Month = (
            calendar.month_name[Today.month-1].upper() if Month == '' else 
            MonthNames[Month] if Month in MonthNames.keys() else Month
        )
        if Month in MonthNames.values():
            break
        print('INVALID Month Name, TRY AGAIN...')

    cursor.execute(f"""
                SELECT SUM([Total Rent]) FROM
                (
                    SELECT [Total Rent] FROM [Monthly Report Data] WHERE [For The Month Of] = '{Month}' AND [Year (YYYY)] = '{Year}'
                    UNION ALL
                    SELECT [Total Rent] FROM [Unusual Occupancy Details] WHERE [For The Month Of] = '{Month}' AND [Year (YYYY)] = '{Year}'
                );
    """)
    TotalCashReceived = int(cursor.fetchone()[0])
    TotalCashReceived = '{:,}'.format(TotalCashReceived)
    print(f'\n>> Total Cash Received For The Month Of {Month}:', TotalCashReceived, '\n')


def GetDetails(WhatToGet: str, DataType = str, PossibleValues = []):
    while True:
        RawData = input(f'\nEnter The {WhatToGet}: ').strip().upper()
        try:
            ConvertedData = DataType(RawData)
            if not PossibleValues or ConvertedData in PossibleValues: 
                return ConvertedData
            else:
                print(f'INVALID {WhatToGet}, TRY AGAIN...')
        except ValueError:
            print(f'INVALID {WhatToGet}, TRY AGAIN...')
