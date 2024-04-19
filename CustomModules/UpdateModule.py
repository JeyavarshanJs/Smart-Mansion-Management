import datetime, calendar
import math
from prettytable import PrettyTable

from CustomModules.VariablesModule import *
from CustomModules.EstablishConnection import *


def Update_DUEAmount_Field():
    PenultimateMonth, _, _, Year = Get_DateTime()    

    print("\n\n----ENTER 'STOP' TO QUIT | 'VIEW TABLE' TO VIEW TABLE----")
    while True:
        TenantID = input('\nEnter The Tenant ID: ').strip().upper()
        if TenantID == 'STOP':
            print()
            break
        elif TenantID == 'VIEW TABLE':
            cursor.execute(f"SELECT * FROM [DUE Details] WHERE [For The Month Of] = '{PenultimateMonth}' AND [Year (YYYY)] = '{Year}' AND NOT [DUE Amount] = 0;")
            Records = cursor.fetchall()

            Table = PrettyTable()
            Table.field_names = ['Tenant ID', 'Tenant Name', 'Room/Shop ID', 'DUE Amount', 'For The Month Of', 'Year']
            Table.align['Tenant Name'] = 'l'
            for Record in Records:
                Record[3] = int(Record[3])
                Table.add_row(Record)

            print('\n', Table, sep='')
            print()
            continue
        elif TenantID.isdigit():
            TenantID = "{:04d}".format(int(TenantID))
            cursor.execute(f"SELECT ID FROM [Tenant's Information] WHERE ID = '{TenantID}';")
            if cursor.fetchone is None:
                print('No Records Found, TRY AGAIN...')
                continue
        else:
            print('INVALID Tenant ID, TRY AGAIN...')
            continue

        DUE_Amount = input('\nEnter DUE Amount: ').strip().upper()
        if DUE_Amount.isdigit():
            cursor.execute(f"UPDATE [DUE Details] SET [DUE Amount] = {DUE_Amount} WHERE [Tenant ID] = '{TenantID}';")
            cursor.commit()
        else:
            print('INVALID DUE Amount, TRY AGAIN...')

    print("\n>>> 'DUE Amount' UPDATED Successfully <<<\n")

def Update_TotalRent_Field():
    def UpdateRecord(Record, GetTenantCount = False):
        ID = Record[0]
        if GetTenantCount:
            while True:
                TenantCount = input(f'\nEnter Tenant Count For The Room/Shop (ID: {ID}): ') if ID in Room_IDs else '1'
                if TenantCount.isdigit():
                    TenantCount = int(TenantCount)
                    break
                else:
                    print('INVALID Tenant Count, TRY AGAIN...')
        else:
            TenantCount = Record[1]

        Room_Rent = Record[TenantCount+1] if TenantCount != 0 else 0
        Other_Charges = Record[TenantCount+4] if TenantCount != 0 else 0
        Current_Charge = Record[8]

        cursor.execute(f"SELECT [Number Of Days Occupied], [Closing Sub-Meter Reading], [Opening Sub-Meter Reading] \
                    FROM [Monthly Report Data] WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
        Data = cursor.fetchone()
        Days_Occupied = Data[0]
        Closing_Reading = Data[1]
        Opening_Reading = Data[2]
        if ID in Room_IDs:
            Total_Rent = math.ceil((Room_Rent + Other_Charges) * Days_Occupied / 30) + math.ceil((Closing_Reading - Opening_Reading)*float(Current_Charge)) \
                + math.ceil(TotalWaterCharge / TotalTenantCount * TenantCount) if TenantCount != 0 else 0
        else:
            Total_Rent = math.ceil((Room_Rent + Other_Charges) * Days_Occupied / 30) + math.ceil((Closing_Reading - Opening_Reading)*float(Current_Charge)) if TenantCount != 0 else 0

        cursor.execute(f"UPDATE [Monthly Report Data] SET [Total Rent] = ? WHERE [Room/Shop ID] = ? AND \
                    [For The Month Of] = '{Month}';", (Total_Rent, ID))
        con.commit()

    PenultimateMonth, Month = Get_DateTime()
    
    # TOTAL TENANT COUNT
    if Month == PenultimateMonth:
        cursor.execute("SELECT [Room/Shop ID], [Tenant Count] FROM [Room/Shop Data]")
        Records = cursor.fetchall()
        TotalTenantCount = sum(
            Record[1] if Record[0] in Room_IDs else 0 for Record in Records
        )
    else:
        while True:
            TotalTenantCount = input(f'\nEnter Total Tenant Count For The Month Of {Month}: ')
            TotalTenantCount = 1 if TotalTenantCount == '' else int(TotalTenantCount) if TotalTenantCount.isdigit() else None
            if TotalTenantCount is None:
                print('INVALID Total Tenant Count, TRY AGAIN...')

    cursor.execute(f"SELECT SUM([Amount]) FROM [Water Purchase Details] WHERE [For The Month Of] = '{Month}'")
    Data = cursor.fetchone()
    TotalWaterCharge = math.ceil(Data[0]) if Data[0] != None else 0

    if Month == PenultimateMonth:
        cursor.execute("SELECT * FROM [Room/Shop Data] ORDER BY [Room/Shop ID]")
        Records = cursor.fetchall()
        for Record in Records:
            UpdateRecord(Record)
    else:
        print('\nSelect An OPTION:')
        Options = ['Update Total Rent For ALL', 'Update Total Rent For SPECIFIC']
        print(*[f"{i+1}) {_}" for i, _ in enumerate(Options)], sep='\n') 

        while True:
            User_Choice = input('Enter Your Choice ID: ')
            if User_Choice in [str(i+1) for i in range(len(Options))]:
                User_Choice = int(User_Choice)
                break
            else:
                print('ID Not Defined, TRY AGAIN...')

        if User_Choice == 1:
            cursor.execute("SELECT * FROM [Room/Shop Data] ORDER BY [Room/Shop ID]")
            Records = cursor.fetchall()
            for Record in Records:
                UpdateRecord(Record, True)
        elif User_Choice == 2:
            while True:
                IsRunning, ID_List = GenerateList('Room/Shop IDs (eg. 201-205, A3)')
                if not IsRunning:
                    if any(ID not in list(Room_IDs + Shop_IDs) for ID in ID_List):
                        print('Some Room/Shop ID Are NOT VALID, TRY AGAIN...')  
                    else:
                        break    

            for ID in ID_List:
                cursor.execute(f"SELECT * FROM [Room/Shop Data] WHERE [Room/Shop ID] = '{ID}';")
                UpdateRecord(Record, True)

    print("\n>>> 'Total Rent' UPDATED Successfully <<<\n")

def Update_IndividualRent_Field():
    def UpdateRecord(Record, GetTenantCount = False):
        ID = Record[0]
        cursor.execute(f"SELECT [Total Rent] FROM [Monthly Report Data] WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
        TotalRent = cursor.fetchone()[0]

        # Tenant Count
        if GetTenantCount:
            while True:
                TenantCount = input(f'\nEnter Tenant Count For The Room/Shop (ID: {ID}): ') if ID in Room_IDs else '1'
                if TenantCount in ['1', '2', '3']:
                    TenantCount = int(TenantCount)
                    break
                else:
                    print('INVALID Tenant Count, TRY AGAIN...')
        else:
            cursor.execute(f"SELECT [Tenant Count] FROM [Room/Shop Data] WHERE [Room/Shop ID] = '{ID}';")
            TenantCount = cursor.fetchone()[0] if ID in Room_IDs else 1

        cursor.execute(f"SELECT [Tenant ID] FROM [Payment Details] WHERE [For The Month Of] = '{Month}' AND [Room/Shop ID] = '{ID}';")
        TenantIDs = cursor.fetchall()
        for TenantID, in TenantIDs:
            cursor.execute(f"SELECT [DUE Amount] FROM [DUE Details] WHERE [Tenant ID] = '{TenantID}' AND [For The Month Of] = '{PreviousMonth}';")
            RawData = cursor.fetchone()
            BalanceDue = int(RawData[0]) if RawData != None else 0

            IndividualRent = math.ceil(TotalRent / TenantCount) + BalanceDue

            cursor.execute(f"UPDATE [Payment Details] SET [Individual Rent] = '{IndividualRent}' WHERE [Tenant ID] = ? AND [Room/Shop ID] = '{ID}' AND \
                        [For The Month Of] = '{Month}';", (TenantID,))
            con.commit()

    PenultimateMonth, Month, PreviousMonth, Year = Get_DateTime()

    if Month == PenultimateMonth:
        cursor.execute(f"SELECT DISTINCT [Room/Shop ID] FROM [Payment Details] WHERE [For The Month Of] = '{Month}' ORDER BY [Room/Shop ID];")
        Records = cursor.fetchall()
        for Record in Records:
            UpdateRecord(Record)
    else:
        print('\nSelect An OPTION:')
        Options = ['Update Individual Rent For ALL', 'Update Individual Rent For SPECIFIC']
        print(*[f"{i+1}) {_}" for i, _ in enumerate(Options)], sep='\n') 

        while True:
            User_Choice = input('Enter Your Choice ID: ')
            if User_Choice in [str(i+1) for i in range(len(Options))]:
                User_Choice = int(User_Choice)
                break
            else:
                print('ID Not Defined, TRY AGAIN...')

        if User_Choice == 1:
            cursor.execute(f"SELECT DISTINCT [Room/Shop ID] FROM [Payment Details] WHERE [For The Month Of] = '{Month}' ORDER BY [Room/Shop ID];")
            Records = cursor.fetchall()
            for Record in Records:
                UpdateRecord(Record, True)
        elif User_Choice == 2:
            while True:
                IsRunning, ReceiptNumber_List = GenerateList('Receipt Numbers (eg. 11-22, 25)')
                if not IsRunning:
                    for ReceiptNumber in ReceiptNumber_List:
                        cursor.execute(f"SELECT * FROM [Payment Details] WHERE [Receipt Number] = {ReceiptNumber} AND [Year (YYYY)] = '{Year}';")
                        if cursor.fetchone() is None:
                            print('Some Room/Shop ID Are NOT VALID, TRY AGAIN...')  
                            break
                    else:
                        break    

            for ReceiptNumber in ReceiptNumber_List:
                cursor.execute(f"SELECT [Room/Shop ID] FROM [Payment Details] WHERE [For The Month Of] = '{Month}' AND [Receipt Number] = {ReceiptNumber};")
                UpdateRecord(cursor.fetchone[0])

    print("\n>>> 'Individual Rent' UPDATED Successfully <<<\n")

def Update_TenantsCount_Field():
    cursor.execute('UPDATE [Room/Shop Data] SET [Tenant Count] = 0;')
    con.commit()
    cursor.execute("SELECT [Room/Shop ID], COUNT(*) FROM [Occupancy Information] WHERE [To (Date)] IS NULL GROUP BY [Room/Shop ID];")
    Records = cursor.fetchall()
    for Record in Records:
        ID = Record[0]
        Tenant_Count = Record[1]
        cursor.execute('UPDATE [Room/Shop Data] SET [Tenant Count] = ? WHERE [Room/Shop ID] = ?;', (Tenant_Count, ID))
        con.commit()
    print("\n>>> 'Tenant Count' UPDATED Successfully <<<\n")

def Update_CurrentStatus_Field():
    cursor.execute("SELECT [ID] FROM [Tenant's Information];")
    TenantIDs = cursor.fetchall()
    for TenantID, in TenantIDs:
        cursor.execute(f"SELECT [Room/Shop ID] FROM [Occupancy Information] WHERE [Tenant ID] = '{TenantID}' AND [To (Date)] IS NULL")
        x = cursor.fetchall()
        if x == []:
            cursor.execute(f"UPDATE [Tenant's Information] SET [Current Status] = 'VACATED' WHERE [ID] = '{TenantID}'")
        else:
            cursor.execute(f"UPDATE [Tenant's Information] SET [Current Status] = 'OCCUPIED' WHERE [ID] = '{TenantID}'")
        cursor.commit()
    print("\n>>> 'Current Status' UPDATED Successfully <<<\n")

def Update_ClosingReading_Field():
    def DisplayUpdatedRecords():
        cursor.execute(f"SELECT [Room/Shop ID], [Closing Sub-Meter Reding], [Opening Sub-Meter Reding] FROM [Monthly Report Data] \
                        WHERE [For The Month Of] = '{Month}'")
        RawRecords = cursor.fetchall()
        
        Table = PrettyTable()
        Table.field_names = ['Room/Shop Data', 'Closing Sub-Meter Reading', 'Opening Sub-Meter Reading']
        
        for Record in RawRecords:
            Record[1] = round(Record[1], 1)
            Record[2] = round(Record[2], 1)
            Table.add_row(Record)

        print('\n', Table, sep='')
        EditRecords()

    def EditRecords():
        UserPreference = input('\nDo You Want To Edit Any Record? (Y/N): ').strip().upper()
        if UserPreference in ['Y', '']:
            print("\n\n----ENTER 'STOP' TO QUIT----")
            IsRunning = True
            while IsRunning:
                while True:
                    ID = input('\nEnter Room/Shop ID To Edit: ').strip().upper()
                    if ID in list(Shop_IDs + Room_IDs):
                        break
                    elif ID == 'STOP':
                        IsRunning = False
                        break
                    else:
                        print('INVALID Room/Shop ID, TRY AGAIN...')

                if IsRunning:
                    ClosingReading = input(f"\nEnter 'Closing Sub-Meter Reading' For The Room/Shop (ID: {ID}): ").strip()
                    try:
                        ClosingReading = round(float(ClosingReading), 1)
                        break
                    except ValueError:
                        print("INVALID 'Closing Sub-Meter Reading', TRY AGAIN...")

                    cursor.execute(f"UPDATE [Monthly Report Data] SET [Closing Sub-Meter Reading] = {ClosingReading} WHERE [Room/Shop ID] = '{ID}' \
                                    AND [For The Month Of] = '{Month}';")
                    cursor.commit()
                else:
                    DisplayUpdatedRecords()

    print('\n>> Fill The BLANK With Appropriate Value <<')
    print('I Want To ________ Closing Sub-Meter Reading.')
    Options = ['UPDATE', 'EDIT']
    print(f'{i+1}) {_}' for i, _ in enumerate(Options))
    
    while True:
        User_Choice = input('Enter Your Choice ID: ')
        if User_Choice in [str(i+1) for i in range(len(Options))]:
            User_Choice = int(User_Choice)
            break
        else:
            print('ID Not Defined, TRY AGAIN...')
    
    if User_Choice == 1:
        Today = datetime.date.today()
        Month = calendar.month_name[Today.month].upper()
        cursor.execute(f"SELECT [Room/Shop ID] FROM [Monthly Report Data] WHERE [For The Month Of] = '{Month}' AND [Closing Sub-Meter Reading] IS NULL")
        IDs = cursor.fetchall()

        if all(_ in IDs for _ in list(Shop_IDs + Room_IDs)):
            for ID in list(Shop_IDs + Room_IDs):
                while True:
                    ClosingReading = input(f"\nEnter 'Closing Sub-Meter Reading' For The Room/Shop (ID: {ID}): ").strip()
                    try:
                        ClosingReading = round(float(ClosingReading), 1)
                        break
                    except ValueError:
                        print("INVALID 'Closing Sub-Meter Reading', TRY AGAIN...")

                cursor.execute(f"UPDATE [Monthly Report Data] SET [Closing Sub-Meter Reading] = {ClosingReading} WHERE [Room/Shop ID] = '{ID}' \
                                AND [For The Month Of] = '{Month}';")
                cursor.commit()

            DisplayUpdatedRecords()

        elif any(_ in IDs for _ in list(Shop_IDs + Room_IDs)):
            print('\n', '-' * 50, sep='')
            print('Some Records Are MISSING To Update, Check Your Database And TRY AGAIN...')
            print('-' * 50, '\n', sep='')

        else:
            print('\n', '-' * 50, sep='')
            print('NO Records FOUND To Update, Check Your Database And TRY AGAIN...')
            print('-' * 50, '\n', sep='')
    print("\n>>> 'Closing Sub-Meter Reading' UPDATED Successfully <<<\n")

def Update_NumberOfDaysOccupied_Field():
    def DisplayRecords():
        cursor.execute(f"SELECT [Room/Shop ID], [Number Of Days Occupied] FROM [Monthly Report Data] WHERE [For The Month Of] = '{Month}'")
        Records = cursor.fetchall()
        
        Table = PrettyTable()
        Table.field_names = ['Room/Shop Data', 'Number Of Days Occupied']
        Table.add_rows(Records)

        print('\n', Table, sep='')
        EditRecords()

    def EditRecords():
        UserPreference = input('\nDo You Want To Edit Any Record? (Y/N): ').strip().upper()
        if UserPreference in ['Y', '']:
            print("\n\n----ENTER 'STOP' TO QUIT----")
            IsRunning = True
            while IsRunning:
                while True:
                    ID = input('\nEnter Room/Shop ID To Edit: ').strip().upper()
                    if ID in list(Shop_IDs + Room_IDs):
                        break
                    elif ID == 'STOP':
                        IsRunning = False
                        break
                    else:
                        print('INVALID Room/Shop ID, TRY AGAIN...')

                if IsRunning:
                    NumberOfDaysOccupied = input(f"\nEnter 'Number Of Days Occupied' For The Room/Shop (ID: {ID}): ").strip()
                    if NumberOfDaysOccupied in [str(_) for _ in range(31)]:
                        NumberOfDaysOccupied = int(NumberOfDaysOccupied)
                        break
                    else:
                        print("INVALID Entry, TRY AGAIN...")

                    cursor.execute(f"UPDATE [Monthly Report Data] SET [Number Of Days Occupied] = {NumberOfDaysOccupied} WHERE \
                                    [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
                    cursor.commit()
                else:
                    DisplayRecords()
        elif UserPreference != 'N':
            print('INVALID Choice, TRY AGAIN...')
            EditRecords()

    Today = datetime.date.today()
    Month = calendar.month_name[Today.month].upper()
    cursor.execute(f"SELECT [Room/Shop ID] FROM [Monthly Report Data] WHERE [For The Month Of] = '{Month}'")
    IDs = cursor.fetchall()

    if all(_ in IDs for _ in list(Shop_IDs + Room_IDs)):
        DisplayRecords()

    elif any(_ in IDs for _ in list(Shop_IDs + Room_IDs)):
        print('\n', '-' * 50, sep='')
        print('Some Records Are MISSING To Update, Check Your Database And TRY AGAIN...')
        print('-' * 50, '\n', sep='')

    else:
        print('\n', '-' * 50, sep='')
        print('NO Records FOUND To Update, Check Your Database And TRY AGAIN...')
        print('-' * 50, '\n', sep='')
    print("\n>>> 'Number Of Days Occupied' UPDATED Successfully <<<\n")


# OTHER FUNCTIONS
def Get_DateTime(GetMonth = True):
    Today = datetime.date.today()
    PenultimateMonth = calendar.month_name[Today.month-1].upper()
    PreviousMonth = list(MonthNames.values())[(list(MonthNames.values()).index(Month))-1]
    Year = Today.strftime('%Y')
    if GetMonth:
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
    return PenultimateMonth, Month, PreviousMonth, Year

def GenerateList(WhatToGet):
    Elements = input(f'\nEnter The {WhatToGet}: ').upper()
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

            List.extend([str(_) for _ in range(Start, End+1)])
        else:
            List.append(i)
    return False, List
