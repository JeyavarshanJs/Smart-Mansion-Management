import datetime, calendar
import math
from prettytable import PrettyTable

from CustomModules.VariablesModule import *
from CustomModules.EstablishConnection import *


def Update_TenantName_Field(TableName):
    # OCCUPANCY INFORMATION
    if TableName == SUB_MENU_UPDATE_TenantName[1]:
        cursor.execute("SELECT [Tenant ID] FROM [Occupancy Information] WHERE [Tenant ID] IS NOT NULL order by [room/shop id];")
        Records = cursor.fetchall()
        for Record in Records:
            ID = Record[0]
            cursor.execute(f"SELECT [Full Name] FROM [Tenant's Information] WHERE ID = '{ID}';")
            RawData = cursor.fetchone()
            TenantName = RawData[0] if RawData != None else None
            if TenantName != None:
                cursor.execute(f"UPDATE [Occupancy Information] SET [Tenant Name] = '{TenantName}' WHERE [Tenant ID] = ?;", (ID,))
                con.commit()

    # PAYMENT DETAILS
    elif TableName == SUB_MENU_UPDATE_TenantName[2]:
        cursor.execute("SELECT [Tenant ID] FROM [Payment Details] WHERE [Tenant Name] IS NULL;")
        Records = cursor.fetchall()
        for Record in Records:
            ID = Record[0]
            cursor.execute(f"SELECT [Full Name] FROM [Tenant's Information] WHERE ID = '{ID}';")
            RawData = cursor.fetchone()
            TenantName = RawData[0] if RawData != None else None
            if TenantName != None:
                cursor.execute(f"UPDATE [Payment Details] SET [Tenant Name] = '{TenantName}' WHERE [Tenant ID] = ?;", (ID,))
                con.commit()

    print("\n>>> 'Tenant Name' UPDATED Successfully <<<\n")

def Update_TotalRent_Field():
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

    # TOTAL TENANT COUNT
    if Month == calendar.month_name[Today.month-1].upper():
        TotalTenantCount = 0
        cursor.execute(f"SELECT [Room/Shop ID], [Tenant Count] FROM [Room/Shop Data]")
        Records = cursor.fetchall()
        for Record in Records:
            TotalTenantCount += Record[1] if Record[0] in Room_IDs else 0
    else:
        while True:
            TotalTenantCount = input(f'\nEnter Total Tenant Count For The Month Of {Month}: ')
            if TotalTenantCount == '':
                TotalTenantCount = 1
                break
            elif TotalTenantCount.isdigit():
                TotalTenantCount = int(TotalTenantCount)
                break
            else:
                print('INVALID Total Tenant Count, TRY AGAIN...')

    cursor.execute(f"SELECT SUM([Amount]) FROM [Water Purchase Details] WHERE [For The Month Of] = '{Month}'")
    Data = cursor.fetchone()
    TotalWaterCharge = math.ceil(Data[0]) if Data[0] != None else 0
    
    if Month == calendar.month_name[Today.month-1].upper():
        cursor.execute("SELECT * FROM [Room/Shop Data] ORDER BY [Room/Shop ID]")
        Records = cursor.fetchall()
        for Record in Records:
            ID = Record[0]
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
                ID = Record[0]
                while True:
                    TenantCount = input(f'\nEnter Tenant Count For The Room/Shop (ID: {ID}): ') if ID in Room_IDs else '1'
                    if TenantCount.isdigit():
                        TenantCount = int(TenantCount)
                        break
                    else:
                        print('INVALID Tenant Count, TRY AGAIN...')

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
        
        elif User_Choice == 2:
            IsRunning = True
            while IsRunning:
                IDs = input('\nEnter The Receipt NOs (eg. 201-205, A3): ').upper()
                a = IDs.split(',')
                for i in range(len(a)):
                    a[i] = a[i].strip()

                ID_List = []
                for i in a:
                    if '-' in i:
                        StartID, EndID = i.split('-')
                        if StartID.strip().isdigit() and EndID.strip().isdigit():
                            StartID, EndID = int(StartID.strip()), int(EndID.strip())
                            IsRunning = False
                        else:
                            print('INVALID Receipt Numbers, TRY AGAIN...')
                            IsRunning = True
                            break
                        ID_List.extend([str(_) for _ in range(StartID, EndID+1)])
                    else:
                        ID_List.append(i)
                        IsRunning = False
                if not IsRunning:
                    for i in ID_List:
                        if i not in list(Room_IDs + Shop_IDs):
                            print('Some Room ID Are NOT VALID, TRY AGAIN...')      
                            IsRunning = True      
                            break

            for ID in ID_List:
                cursor.execute(f"SELECT * FROM [Room/Shop Data] WHERE [Room/Shop ID] = '{ID}';")
                Record = cursor.fetchone()
                ID = Record[0]
                while True:
                    TenantCount = input(f'\nEnter Tenant Count For The Room/Shop (ID: {ID}): ') if ID in Room_IDs else '1'
                    if TenantCount.isdigit():
                        TenantCount = int(TenantCount)
                        break
                    else:
                        print('INVALID Tenant Count, TRY AGAIN...')

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
                print(ID, Total_Rent)
                cursor.execute(f"UPDATE [Monthly Report Data] SET [Total Rent] = ? WHERE [Room/Shop ID] = ? AND \
                            [For The Month Of] = '{Month}';", (Total_Rent, ID))
                con.commit()

    print("\n>>> 'Total Rent' UPDATED Successfully <<<\n")

def Update_IndividualRent_Field():
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
    PreviousMonth = list(MonthNames.values())[(list(MonthNames.values()).index(Month))-1]

    cursor.execute(f"SELECT [Tenant ID], [Room/Shop ID] FROM [Payment Details] WHERE [For The Month Of] = '{Month}' ORDER BY [Room/Shop ID];")
    Records = cursor.fetchall()
    for Record in Records:
        TenantID = Record[0]        
        ID = Record[1]

        cursor.execute(f"SELECT [Total Rent] FROM [Monthly Report Data] WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
        TotalRent = cursor.fetchone()[0]

        # Tenant Count
        if Month == calendar.month_name[Today.month-1].upper():
            cursor.execute(f"SELECT [Tenant Count] FROM [Room/Shop Data] WHERE [Room/Shop ID] = '{ID}';")
            TenantCount = cursor.fetchone()[0] if ID in Room_IDs else 1
        else:
            while True:
                TenantCount = input(f'\nEnter Tenant Count For The Room/Shop (ID: {ID}): ') if ID in Room_IDs else '1'
                if TenantCount in ['1', '2', '3']:
                    TenantCount = int(TenantCount)
                    break
                else:
                    print('INVALID Tenant Count, TRY AGAIN...')

        cursor.execute(f"SELECT [DUE Amount] FROM [DUE Details] WHERE [Tenant ID] = '{TenantID}' AND [For The Month Of] = '{PreviousMonth}';")
        RawData = cursor.fetchone()
        BalanceDue = int(RawData[0]) if RawData != None else 0

        IndividualRent = math.ceil(TotalRent / TenantCount) + BalanceDue

        cursor.execute(f"UPDATE [Payment Details] SET [Individual Rent] = '{IndividualRent}' WHERE [Tenant ID] = ? AND [Room/Shop ID] = '{ID}' AND \
                       [For The Month Of] = '{Month}';", (TenantID,))
        con.commit()
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
    for TenantID in TenantIDs:
        cursor.execute(f"SELECT [Room/Shop ID] FROM [Occupancy Information] WHERE [Tenant ID] = '{TenantID[0]}' AND [To (Date)] IS NULL")
        x = cursor.fetchall()
        if x == []:
            cursor.execute(f"UPDATE [Tenant's Information] SET [Current Status] = 'VACATED' WHERE [ID] = '{TenantID[0]}'")
            cursor.commit()
        else:
            cursor.execute(f"UPDATE [Tenant's Information] SET [Current Status] = 'OCCUPIED' WHERE [ID] = '{TenantID[0]}'")
            cursor.commit()
    print("\n>>> 'Current Status' UPDATED Successfully <<<\n")

def Update_ForTheMonthOf_Field_WaterPurchaseDetails():
    cursor.execute("SELECT [Purchase Date] FROM [Water Purchase Details] WHERE [For The Month Of] IS NULL")
    Records = cursor.fetchall()
    for Record in Records:
        Date = datetime.datetime.strptime(str(Record[0])[:10], r'%Y-%m-%d')
        Month = Date.strftime('%B').upper()
        cursor.execute(f"UPDATE [Water Purchase Details] SET [For The Month Of] = '{Month}' WHERE [Purchase Date] = ?", (Date,))
        cursor.commit()    
    print("\n>>> 'For The Month Of' Field In 'Water Purchase Details' UPDATED Successfully <<<\n")

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
        if UserPreference == 'Y' or UserPreference == '':
            print("\n\n----ENTER 'STOP' TO QUIT----")
            IsRunning = True
            while IsRunning:
                while True:
                    ID = input('\nEnter Room/Shop ID To Edit: ').strip().upper()
                    if ID in list(Shop_IDs + Room_IDs):
                        break
                    elif ID == 'STOP':
                        IsRunning == False
                        break
                    else:
                        print('INVALID Room/Shop ID, TRY AGAIN...')

                if IsRunning == True:
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
        if UserPreference == 'Y' or UserPreference == '':
            print("\n\n----ENTER 'STOP' TO QUIT----")
            IsRunning = True
            while IsRunning:
                while True:
                    ID = input('\nEnter Room/Shop ID To Edit: ').strip().upper()
                    if ID in list(Shop_IDs + Room_IDs):
                        break
                    elif ID == 'STOP':
                        IsRunning == False
                        break
                    else:
                        print('INVALID Room/Shop ID, TRY AGAIN...')

                if IsRunning == True:
                    NumberOfDaysOccupied = input(f"\nEnter 'Number Of Days Occupied' For The Room/Shop (ID: {ID}): ").strip()
                    if NumberOfDaysOccupied in ['15', '30']:
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
