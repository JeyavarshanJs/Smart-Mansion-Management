import datetime, calendar, math
import os, winsound
from prettytable import PrettyTable

from CustomModules.VariablesModule import *
from CustomModules.EstablishConnection import *
from CustomModules.FetchDataModule import *
from CustomModules.DataHandlingModule import *

Today = datetime.date.today()
Year = Today.strftime('%Y')

def Update_TotalRent_Field(GetMonth = True):
    Month, _ = Get_DateTime() if GetMonth else (calendar.month_name[Today.month-1].upper(), None)

    # TOTAL TENANT COUNT
    cursor.execute(f"SELECT [Room/Shop ID], [Tenant Count] FROM [Monthly Report Data] WHERE [For The Month Of] = '{Month}' AND [Year (YYYY)] = '{Year}'")
    Records = cursor.fetchall()
    if any(Record[1] is None for Record in Records):
        print('\n', '-' * 50, sep='')
        print(">> Update 'Tenant Count' Field PROPERLY <<")
        print('-' * 50, '\n', sep='')
        winsound.Beep(1000, 500)
        return
    else:
        TotalTenantCount = sum(
            Record[1] for Record in Records if Record[0] in Room_IDs
        )

    cursor.execute(f"SELECT SUM([Amount]) FROM [Water Purchase Details] WHERE [For The Month Of] = '{Month}'")
    Data = cursor.fetchone()
    TotalWaterCharge = math.ceil(Data[0]) if Data[0] != None else 0

    cursor.execute(f"SELECT [Room/Shop ID], [Days Occupied], [Tenant Count], [Closing Sub-Meter Reading], [Opening Sub-Meter Reading] FROM [Monthly Report Data] \
                     WHERE [For The Month Of] = '{Month}' AND [Year (YYYY)] = '{Year}';")
    Records = cursor.fetchall()
    for ID, DaysOccupied, TenantCount, Closing_Reading, Opening_Reading in Records:
        cursor.execute(f"SELECT * FROM [Room/Shop Data] WHERE [Room/Shop ID] = '{ID}';")
        Record = cursor.fetchone()
        RoomRent, OtherCharges, CurrentCharge = Record[TenantCount], Record[TenantCount+3], Record[8]

        if ID in Room_IDs:
            Total_Rent = math.ceil((RoomRent + OtherCharges) * DaysOccupied / 30) + math.ceil((Closing_Reading - Opening_Reading)*float(CurrentCharge)) \
                + math.ceil(TotalWaterCharge / TotalTenantCount * TenantCount) if TenantCount != 0 else 0
        else:
            Total_Rent = math.ceil((RoomRent + OtherCharges) * DaysOccupied / 30) + math.ceil((Closing_Reading - Opening_Reading)*float(CurrentCharge)) if TenantCount != 0 else 0

        cursor.execute(f"UPDATE [Monthly Report Data] SET [Total Rent] = ? WHERE [Room/Shop ID] = ? AND [For The Month Of] = '{Month}' AND [Year (YYYY)] = '{Year}';", (Total_Rent, ID))
        con.commit()

    print("\n>>> 'Total Rent' UPDATED Successfully <<<\n")
    return Month

def Update_IndividualRent_Field(Month = None):
    Month, PreviousMonth = Get_DateTime(Month)

    cursor.execute(f"SELECT [Room/Shop ID], [Tenant ID] FROM [Payment Details] WHERE [For The Month Of] = '{Month}' AND [Year (YYYY)] = '{Year}';")
    Records = cursor.fetchall()
    for ID, TenantID in Records:
        cursor.execute(f"SELECT [Tenant Count], [Total Rent] FROM [Monthly Report Data] WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}' AND [Year (YYYY)] = '{Year}';")
        TenantCount, TotalRent = cursor.fetchone()
        if TotalRent is None:
            print('\n', '-' * 50, sep='')
            print(">> Update 'Total Rent' Field PROPERLY <<")
            print('-' * 50, '\n', sep='')
            winsound.Beep(1000, 500)
            return

        cursor.execute(f"SELECT [DUE Amount] FROM [DUE Details] WHERE [Tenant ID] = '{TenantID}' AND [For The Month Of] = '{PreviousMonth}' AND [Year (YYYY)] = '{Year}';")
        RawData = cursor.fetchone()
        BalanceDue = int(RawData[0]) if RawData != None else 0

        IndividualRent = math.ceil(TotalRent / TenantCount) + BalanceDue

        cursor.execute(f"UPDATE [Payment Details] SET [Individual Rent] = '{IndividualRent}' WHERE [Tenant ID] = '{TenantID}' AND [Room/Shop ID] = '{ID}' \
                         AND [For The Month Of] = '{Month}' AND [Year (YYYY)] = '{Year}';")
        con.commit()

    print("\n>>> 'Individual Rent' UPDATED Successfully <<<\n")
    winsound.Beep(1000, 500)

def Update_DUEAmount_Field():
    PenultimateMonth = calendar.month_name[Today.month-1].upper()

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

            print('\n', Table, '\n', sep='')
        elif TenantID == 'FIND TENANT ID':
            print('\n<<<<+>>>>')
            FetchData_TenantID_FROM_TenantName(False)
            print('\n<<<<+>>>>\n')
        elif TenantID.isdigit():
            TenantID = "{:04d}".format(int(TenantID))
            cursor.execute(f"SELECT * FROM [DUE Details] WHERE [Tenant ID] = '{TenantID}' AND [For The Month Of] = '{PenultimateMonth}' AND [Year (YYYY)] = '{Year}';")
            if cursor.fetchone is not None:
                DUE_Amount = input('\nEnter DUE Amount: ').strip().upper()
                if DUE_Amount.isdigit():
                    cursor.execute(f"UPDATE [DUE Details] SET [DUE Amount] = {DUE_Amount} WHERE [Tenant ID] = '{TenantID}' \
                                     AND [For The Month Of] = '{PenultimateMonth}' AND [Year (YYYY)] = '{Year}';")
                    cursor.commit()
                else:
                    print('>> INVALID DUE Amount, TRY AGAIN <<')
            else:
                print('>> No Records Found, TRY AGAIN <<')
        else:
            print('>> INVALID Tenant ID, TRY AGAIN <<')

    print("\n>>> 'DUE Amount' UPDATED Successfully <<<\n")
    winsound.Beep(1000, 500)

def Update_TenantsCount_Field():
    Month = calendar.month_name[Today.month].upper()
    cursor.execute("SELECT [Room/Shop ID], COUNT(*) FROM [Occupancy Information] WHERE [To (Date)] IS NULL GROUP BY [Room/Shop ID];")
    Records = cursor.fetchall()
    for Record in Records:
        ID, TenantCount = Record
        cursor.execute(f"UPDATE [Monthly Report Data] SET [Tenant Count] = ? WHERE [Room/Shop ID] = ? AND [For The Month Of] = '{Month}' \
                         AND [Year (YYYY)] = '{Year}';", (TenantCount, ID))
        con.commit()
    print("\n>>> 'Tenant Count' UPDATED Successfully <<<\n")
    winsound.Beep(1000, 500)

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
    winsound.Beep(1000, 500)

def Update_ClosingReading_Field():
    def VerifyUpdatedRecords(Month):
        cursor.execute(f"SELECT [Room/Shop ID], [Closing Sub-Meter Reading], [Opening Sub-Meter Reading] FROM [Monthly Report Data] \
                         WHERE [For The Month Of] = '{Month}' AND [Year (YYYY)] = '{Year}';")
        RawRecords = cursor.fetchall()

        for Record in RawRecords:
            Table = PrettyTable()
            Table.field_names = ['Room/Shop Data', 'Closing Sub-Meter Reading', 'Opening Sub-Meter Reading']
            Record[1] = round(Record[1], 1)
            Record[2] = round(Record[2], 1)
            Table.add_row(Record)
            print('\n', Table, sep='')

            if GetUser_Confirmation('Do You Want To Edit This Record?', ['Y'], ['N', '']):
                UpdateData(Record[0])

    def UpdateData(ID):
        ClosingReading = input(f"\nEnter 'Closing Sub-Meter Reading' For The Room/Shop (ID: {ID}): ").strip()
        try:
            ClosingReading = round(float(ClosingReading), 1)
            cursor.execute(f"SELECT [Opening Sub-Meter Reading] FROM [Monthly Report Data] WHERE [Room/Shop ID] = '{ID}' \
                             AND [For The Month Of] = '{Month}' AND [Year (YYYY)] = '{Year}';")
            OpeningReading = round(float(cursor.fetchone()[0]))
            if ClosingReading < OpeningReading:
                print(">> 'Units Consumed' Cannot Be NEGATIVE, TRY AGAIN <<")
                return UpdateData(ID)
        except ValueError:
            print(">> INVALID 'Closing Sub-Meter Reading', TRY AGAIN <<")
            return UpdateData(ID)

        cursor.execute(f"UPDATE [Monthly Report Data] SET [Closing Sub-Meter Reading] = {ClosingReading} WHERE [Room/Shop ID] = '{ID}' \
            AND [For The Month Of] = '{Month}' AND [Year (YYYY)] = '{Year}';")
        cursor.commit()

    Month = calendar.month_name[Today.month].upper()
    print('\n>> Fill The BLANK With Appropriate Value <<\nI Want To ________ Closing Sub-Meter Reading.')
    Options = ['UPDATE', 'EDIT']
    print('\n'.join([f'{i+1}) {ID}' for i, ID in enumerate(Options)]))

    User_Choice = int(GetDetails('Choice ID', PossibleValues= [str(i+1) for i in range(len(Options))]))
    if User_Choice == 1:
        cursor.execute(f"SELECT [Room/Shop ID] FROM [Monthly Report Data] WHERE [For The Month Of] = '{Month}' AND [Year (YYYY)] = '{Year}' \
                         AND [Closing Sub-Meter Reading] IS NULL")
        RawIDs = cursor.fetchall()
        IDs = [str(ID) for ID, in RawIDs]

        if Check_MRDRecords(IDs):
            for ID in list(Shop_IDs + Room_IDs):
                UpdateData(ID)

            print('\n<<<<<+>>>>>')
            VerifyUpdatedRecords(Month)
            print('\n<<<<<+>>>>>\n')
            print("\n>>> 'Closing Sub-Meter Reading' UPDATED Successfully <<<\n")
            winsound.Beep(1000, 500)

    elif User_Choice == 2:
        print('\n<<<<<+>>>>>')
        VerifyUpdatedRecords(Month)
        print('\n<<<<<+>>>>>\n')
        print("\n>>> 'Closing Sub-Meter Reading' EDITED Successfully <<<\n")
        winsound.Beep(1000, 500)

def Update_DaysOccupied_Field():
    def DisplayRecords(Month):
        Query = f'''
            SELECT MRD.[Room/Shop ID], MRD.[Days Occupied], OI.[Tenant Name], OI.[Shop Name (Optional)], OI.[From (Date)], OI.[To (Date)]
            FROM [Monthly Report Data] MRD
            INNER JOIN [Occupancy Information] OI ON MRD.[Room/Shop ID] = OI.[Room/Shop ID]
            WHERE MRD.[For The Month Of] = ? AND MRD.[Year (YYYY)] = '{Year}'
            ORDER BY MRD.[Room/Shop ID];
        '''
        cursor.execute(Query, (Month,))
        Records = cursor.fetchall()

        PossibleIDs = []
        Table = PrettyTable()
        Table.field_names = ['Room/Shop ID', 'Days Occupied', 'Tenant Name', 'Shop Name', 'From (Date)', 'To (Date)']
        Table.align['Tenant Name'] = 'l'
        for Record in Records:
            OccupiedMonth = calendar.month_name[int(Record[4].strftime('%m'))].upper() if Record[4] is not None else None
            VacatedMonth = calendar.month_name[int(Record[5].strftime('%m'))].upper() if Record[5] is not None else None
            if OccupiedMonth == Month or VacatedMonth == Month:
                PossibleIDs.append(Record[0])
                Record[4] = Record[4].strftime(r'%d-%m-%Y') if Record[4] is not None else ''
                Table.add_row(Record)

        print('\n', Table, sep='')
        EditRecords(Month, PossibleIDs)

    def EditRecords(Month, PossibleIDs):
        if GetUser_Confirmation('Do You Want To Edit The Records?'):
            for ID in PossibleIDs:
                DaysOccupied = int(GetDetails(f"'Days Occupied' For The Room/Shop (ID: {ID})", PossibleValues= [str(ID) for ID in range(31)]))
                cursor.execute(f"UPDATE [Monthly Report Data] SET [Days Occupied] = {DaysOccupied} WHERE [Room/Shop ID] = '{ID}' \
                                 AND [For The Month Of] = '{Month}' AND [Year (YYYY)] = '{Year}';")
                cursor.commit()
            DisplayRecords(Month)

    Month = calendar.month_name[Today.month].upper()
    cursor.execute(f"SELECT [Room/Shop ID] FROM [Monthly Report Data] WHERE [For The Month Of] = '{Month}' AND [Year (YYYY)] = '{Year}'")
    RawIDs = cursor.fetchall()
    IDs = [str(ID) for ID, in RawIDs]

    if Check_MRDRecords(IDs):
        DisplayRecords(Month)
        print("\n>>> 'Days Occupied' UPDATED Successfully <<<\n")
        winsound.Beep(1000, 500)

def Update_ToDate_Field():
    ID = GetDetails('Vacating Room/Shop ID', PossibleValues= list(Shop_IDs + Room_IDs))
    Date = GetDate("'To (Date)'")[0]

    cursor.execute(f"SELECT [Tenant ID], [Tenant Name] FROM [Occupancy Information] WHERE [Room/Shop ID] = '{ID}' AND [To (Date)] IS NULL;")
    Records = cursor.fetchall()
    TenantIDs = [str(Record[0]) for Record in Records]
    Table = PrettyTable()
    Table.field_names = ['Tenant ID', 'Tenant Name']
    Table.align['Tenant Name'] = 'l'
    Table.add_rows(Records)
    print('\n', Table, sep='')

    print("\n\n--- ENTER '' IF EVERYONE IS VACATING ---")
    while True:
        RawData = input('Enter The Vacating Tenant ID(s) (eg. 0033, 0044): ').strip()
        if RawData == '':
            VacatingTenant_List = TenantIDs
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
    for TenantID in VacatingTenant_List:
        cursor.execute(f"UPDATE [Occupancy Information] SET [To (Date)] = ? WHERE [Room/Shop ID] = '{ID}' AND [Tenant ID] = '{TenantID}';", (Date,))
        cursor.commit()
    print("\n>>> 'To (Date)' UPDATED Successfully <<<\n")
    winsound.Beep(1000, 500)
    return VacatingTenant_List, Date

def Update_PermanentData(WhatToUpdate):
    if WhatToUpdate in ['Output Location', 'Database Path']:
        while True:
            PATH = rf'{input(f'\nEnter The {WhatToUpdate}: ')}'
            if os.path.exists(PATH):
                UpdatePermanentData([WhatToUpdate], {WhatToUpdate: PATH})
                print()
                break
            else:
                print(">> Path Doesn't EXISTS, TRY AGAIN <<")
                winsound.Beep(1000, 500)
    else:
        return
    print("\n>>> 'Permanent Data' UPDATED Successfully <<<\n")
    winsound.Beep(1000, 500)


# OTHER FUNCTIONS
def Get_DateTime(Month = None):
    if Month == None:
        while True:
            Month = input('\nEnter The Desired Month (eg. JAN or JANUARY): ').upper()
            Month = (
                calendar.month_name[Today.month-1].upper() if Month == '' else
                MonthNames[Month] if Month in MonthNames.keys() else Month
            )
            if Month in MonthNames.values():
                break
            print('>> INVALID Month Name, TRY AGAIN <<')
    PreviousMonth = list(MonthNames.values())[(list(MonthNames.values()).index(Month))-1]

    return Month, PreviousMonth

def Check_MRDRecords(IDs):
    if all(ID in IDs for ID in list(Shop_IDs + Room_IDs)):
        return True

    elif any(ID in IDs for ID in list(Shop_IDs + Room_IDs)):
        print('\n', '-' * 75, sep='')
        print('Some Records Are MISSING, Check Your Database And TRY AGAIN...')
        print('-' * 75, '\n', sep='')

    else:
        print('\n', '-' * 75, sep='')
        print('NO Records FOUND To Update, Check Your Database And TRY AGAIN...')
        print('-' * 75, '\n', sep='')

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

def GetUser_Confirmation(QString, YES = ['Y', ''], NO = ['N']):
    while True:
        ANS = input('\n' + QString + ' (Y/N): ').strip().upper()
        if ANS in (YES + NO):
            return True if ANS in YES else False
        else:
            print('>> INVALID Response, TRY AGAIN <<')

def GetDate(IString):
    while True:
        Date = input(f"\nEnter The {IString} (DD/MM/YYYY): ").strip()
        Date = Today.strftime(r'%d/%m/%Y') if Date == '' else Date

        try:
            DateOBJ = datetime.datetime.strptime(Date, r'%d/%m/%Y')
            Date = datetime.date.strftime(DateOBJ, r'%Y-%m-%d')
            return Date, DateOBJ
        except Exception:            
            print('INVALID Date, TRY AGAIN...')
