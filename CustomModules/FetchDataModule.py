import datetime, calendar
from prettytable import PrettyTable

from CustomModules.VariablesModule import *
from CustomModules.EstablishConnection import *


def FetchData_TenantName_FROM_TenantID():
    print("\n\n----ENTER 'STOP' TO QUIT----")
    while True:
        TenantID = input('\nEnter The Tenant ID To Fetch Tenant Name: ').strip()
        if TenantID.upper() == 'STOP':
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

def FetchData_TenantID_FROM_TenantName():
    print("\n\n----ENTER 'STOP' TO QUIT----")
    while True:
        TenantName = input('\nEnter The Tenant Name To Fetch ID: ').strip().upper()
        if TenantName == 'STOP':
            break
        cursor.execute(f"SELECT [ID], [Full Name] FROM [Tenant's Information] WHERE [Full Name] LIKE '%{TenantName}%';")
        Records = cursor.fetchall()
        if Records != []:
            for Record in Records:
                print(f"Name: '{Record[1]}'  --->  ID: '{Record[0]}'")
        else:
            print('No Records Found, TRY AGAIN...')

def FetchData_TenantID_FROM_OccupiedSpaceID():
    print("\n\n----ENTER 'STOP' TO QUIT----")
    while True:
        ID = input('\nEnter The Room/Shop ID: ').strip().upper()
        if ID == 'STOP':
            print()
            break
        elif ID not in list(Shop_IDs + Room_IDs):
            print('INVALID Tenant ID, TRY AGAIN...')
            continue

        cursor.execute(f"SELECT [Tenant ID], [Tenant Name] FROM [Occupancy Information] WHERE [Room/Shop ID] = '{ID}' AND [To (Date)] IS NULL;")
        Records = cursor.fetchall()

        if Records != []:
            print(f"Tenant(s) Occupying Room/Shop (ID: {ID}) is(are):")
            for i, Record in enumerate(Records):
                print(f'  {i+1}) {Record[1]}  ({Record[0]})')
        else:
            print('No Records Found, TRY AGAIN...')

def FetchData_ReceiptNumber_FROM_TenantID():
    Today = datetime.date.today() 
    IsRunning = True
    while IsRunning:
        while True:
            Month = input('\nEnter The Desired Month (eg. JAN or JANUARY): ').strip().upper()
            Month = calendar.month_name[Today.month-1].upper() if Month == '' else Month
            if Month in MonthNames.keys():
                Month = MonthNames[Month]
                break
            elif Month in MonthNames.values():
                break
            else:            
                print('INVALID Month Name, TRY AGAIN...')

        print("\n\n----ENTER 'STOP' TO QUIT | 'CHANGE MONTH' TO CHANGE MONTH----")
        while True:
            TenantID = input('\nEnter The Tenant ID: ').strip().upper()
            if TenantID == 'STOP':
                print()
                IsRunning = False
                break
            elif TenantID == 'CHANGE MONTH':
                print()
                break
            elif TenantID.isdigit():
                TenantID = "{:04d}".format(int(TenantID))
            else:
                print('INVALID Tenant ID, TRY AGAIN...')
                continue
                
            cursor.execute(f"SELECT [Receipt Number], [Status] FROM [Payment Details] WHERE [Tenant ID] = '{TenantID}' AND [For The Month Of] = '{Month}';")
            DataS = cursor.fetchall()
            cursor.execute(f"SELECT [Receipt Number], [Status] FROM [Payment Details (NS)] WHERE [Tenant ID] = '{TenantID}' AND [For The Month Of] = '{Month}';")
            DataNS = cursor.fetchall()
            Records = DataS if DataS != [] else DataNS if DataNS != [] else []

            if Records != []:
                print(f"The Receipt Number(s) Correspond To The Tenant (ID: {TenantID}) Is(Are):")
                for i, Record in enumerate(Records):
                    print(f"  {i+1}) {Record[0]}  (Status: {Record[1]})")
            else:
                print('No Records Found, TRY AGAIN...')

def FetchData_UNPAID_Tenants():
    cursor.execute("SELECT [Tenant ID], [Tenant Name], [Room/Shop ID], [Individual Rent], [For The Month OF] \
                   FROM [Payment Details] WHERE Status = 'UNPAID' ORDER BY [For The Month Of], [Room/Shop ID]")
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

    print('\n', DetailsTable, sep='')

    SUMTable = PrettyTable()
    SUMTable.field_names = ['Total DUE', 'For The Month Of']
    cursor.execute("SELECT SUM([Individual Rent]), [For The Month Of] \
                   FROM [Payment Details] WHERE Status = 'UNPAID' GROUP BY [For The Month Of] ORDER BY SUM([Individual Rent]) DESC")
    RawRecords = cursor.fetchall()

    for Record in RawRecords:
        Record = list(Record)
        Record[0] = '{:,}'.format(int(Record[0]))
        SUMTable.add_row(Record)

    print('\n', SUMTable, sep='', end='\n\n')

def FetchData_GetTenantDetails():
    print("\n\n----ENTER 'STOP' TO QUIT----")
    while True:
        print('''\nADD,
            >>  '1-' To Search Tenant With Tenant_ID
            >>  '2- To Search Tenant With Tenant_Name
            >>  '3-' To Search Tenant with Room_ID''')
        Hint = input('Enter Some Hint To Search For Tenant Details: ').strip().upper()
        if Hint.startswith('1-'):
            Hint = Hint[2:].strip()
            cursor.execute(f"SELECT")

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
    Today = datetime.date.today()
    while True:
        Month = input('\nEnter The Desired Month (eg. JAN or JANUARY): ').upper()
        Month = calendar.month_name[Today.month-1].upper() if Month == '' else Month
        if Month in MonthNames.keys():
            Month = MonthNames[Month]
            break
        elif Month in MonthNames.values():
            break
        else:            
            print('INVALID Month Name, TRY AGAIN...')

    cursor.execute(f"SELECT SUM([Total Rent]) FROM [Monthly Report Data] WHERE [For The Month Of] = '{Month}'")
    TotalCashReceived = int(cursor.fetchone()[0])
    TotalCashReceived = '{:,}'.format(TotalCashReceived)
    print(f'\nTotal Cash Received For The Month Of {Month}:', TotalCashReceived, '\n')
