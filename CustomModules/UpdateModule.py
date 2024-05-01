import datetime, calendar
import math
from prettytable import PrettyTable

from CustomModules.VariablesModule import *
from CustomModules.EstablishConnection import *
from CustomModules.FetchDataModule import *

Today = datetime.date.today()


def Update_TotalRent_Field(GetMonth = True):
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

    if GetMonth:
        PenultimateMonth, Month, ID, ID = Get_DateTime()
    else:
        PenultimateMonth, Month, ID, ID = Get_DateTime(calendar.month_name[Today.month-1].upper())

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

    if Month == PenultimateMonth:
        cursor.execute("SELECT * FROM [Room/Shop Data] ORDER BY [Room/Shop ID]")
        Records = cursor.fetchall()
        for Record in Records:
            UpdateRecord(Record)
    else:
        print('\nSelect An OPTION:')
        Options = ['Update Total Rent For ALL', 'Update Total Rent For SPECIFIC']
        print(*[f"{i+1}) {ID}" for i, ID in enumerate(Options)], sep='\n') 

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
                UpdateRecord(cursor.fetchone(), True)

    print("\n>>> 'Total Rent' UPDATED Successfully <<<\n")
    return Month

def Update_IndividualRent_Field(Month = None):
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

    PenultimateMonth, Month, PreviousMonth, Year = Get_DateTime(Month)

    if Month == PenultimateMonth:
        cursor.execute(f"SELECT DISTINCT [Room/Shop ID] FROM [Payment Details] WHERE [For The Month Of] = '{Month}' ORDER BY [Room/Shop ID];")
        Records = cursor.fetchall()
        for Record in Records:
            UpdateRecord(Record)
    else:
        print('\nSelect An OPTION:')
        Options = ['Update Individual Rent For ALL', 'Update Individual Rent For SPECIFIC']
        print(*[f"{i+1}) {ID}" for i, ID in enumerate(Options)], sep='\n') 

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
                UpdateRecord(cursor.fetchone(), True)

    print("\n>>> 'Individual Rent' UPDATED Successfully <<<\n")

def Update_DUEAmount_Field():
    PenultimateMonth, ID, ID, Year = Get_DateTime()    

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
            continue
        elif TenantID == 'FIND TENANT ID':
            print('\n<<<<+>>>>')
            FetchData_TenantID_FROM_TenantName(False)
            print('\n<<<<+>>>>\n')
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
    def VerifyUpdatedRecords(Month):
        cursor.execute(f"SELECT [Room/Shop ID], [Closing Sub-Meter Reading], [Opening Sub-Meter Reading] FROM [Monthly Report Data] WHERE [For The Month Of] = '{Month}';")
        RawRecords = cursor.fetchall()

        for Record in RawRecords:
            Table = PrettyTable()
            Table.field_names = ['Room/Shop Data', 'Closing Sub-Meter Reading', 'Opening Sub-Meter Reading']
            Record[1] = round(Record[1], 1)
            Record[2] = round(Record[2], 1)
            Table.add_row(Record)
            print('\n', Table, sep='')

            if GetUser_Confirmation('Do You Want To Edit Any Record?', ['Y'], ['N', '']):
                UpdateData(Record[0])

    def UpdateData(ID):
        ClosingReading = input(f"\nEnter 'Closing Sub-Meter Reading' For The Room/Shop (ID: {ID}): ").strip()
        try:
            ClosingReading = round(float(ClosingReading), 1)
            cursor.execute(f"SELECT [Opening Sub-Meter Reading] FROM [Monthly Report Data] WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
            OpeningReading = round(float(cursor.fetchone()[0]))
            if ClosingReading < OpeningReading:
                print(">> 'Units Consumed' Cannot Be NEGATIVE, TRY AGAIN <<")
                return UpdateData(ID)
        except ValueError:
            print(">> INVALID 'Closing Sub-Meter Reading', TRY AGAIN <<")
            return UpdateData(ID)

        cursor.execute(f"UPDATE [Monthly Report Data] SET [Closing Sub-Meter Reading] = {ClosingReading} WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
        cursor.commit()

    Month = calendar.month_name[Today.month].upper()
    print('\n>> Fill The BLANK With Appropriate Value <<')
    print('I Want To ________ Closing Sub-Meter Reading.')
    Options = ['UPDATE', 'EDIT']
    print('\n'.join([f'{i+1}) {ID}' for i, ID in enumerate(Options)]))

    User_Choice = int(GetDetails('Choice ID', PossibleValues= [str(i+1) for i in range(len(Options))]))

    if User_Choice == 1:
        cursor.execute(f"SELECT [Room/Shop ID] FROM [Monthly Report Data] WHERE [For The Month Of] = '{Month}' AND [Closing Sub-Meter Reading] IS NULL")
        RawIDs = cursor.fetchall()
        IDs = [str(ID) for ID, in RawIDs]

        if all(ID in IDs for ID in list(Shop_IDs + Room_IDs)):
            for ID in list(Shop_IDs + Room_IDs):
                UpdateData(ID)

            print('\n<<<<<+>>>>>')
            VerifyUpdatedRecords(Month)
            print('\n<<<<<+>>>>>\n')
            print("\n>>> 'Closing Sub-Meter Reading' UPDATED Successfully <<<\n")

        elif any(ID in IDs for ID in list(Shop_IDs + Room_IDs)):
            print('\n', '-' * 75, sep='')
            print('Some Records Are MISSING To Update, Check Your Database And TRY AGAIN...')
            print('-' * 75, '\n', sep='')

        else:
            print('\n', '-' * 75, sep='')
            print('NO Records FOUND To Update, Check Your Database And TRY AGAIN...')
            print('-' * 75, '\n', sep='')

    elif User_Choice == 2:
        print('\n<<<<<+>>>>>')
        VerifyUpdatedRecords(Month)
        print('\n<<<<<+>>>>>\n')
        print("\n>>> 'Closing Sub-Meter Reading' EDITED Successfully <<<\n")

def Update_NumberOfDaysOccupied_Field():
    def DisplayRecords(Month):
        Query = '''
            SELECT MRD.[Room/Shop ID], MRD.[Number Of Days Occupied], OI.[Tenant Name], OI.[Shop Name (Optional)], OI.[From (Date)], OI.[To (Date)]
            FROM [Monthly Report Data] MRD
            INNER JOIN [Occupancy Information] OI ON MRD.[Room/Shop ID] = OI.[Room/Shop ID]
            WHERE MRD.[For The Month Of] = ?
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
                Record[3] = Record[3] if Record[3] is not None else ''
                Record[4] = Record[4].strftime(r'%d-%m-%Y') if Record[4] is not None else ''
                Table.add_row(Record)

        print('\n', Table, sep='')
        EditRecords(Month, PossibleIDs)

    def EditRecords(Month, PossibleIDs):
        if GetUser_Confirmation('Do You Want To Edit The Records?'):
            for ID in PossibleIDs:
                DaysOccupied = int(GetDetails(f"'Number Of Days Occupied' For The Room/Shop (ID: {ID})", PossibleValues= [str(ID) for ID in range(31)]))
                cursor.execute(f"UPDATE [Monthly Report Data] SET [Number Of Days Occupied] = {DaysOccupied} WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
                cursor.commit()
            DisplayRecords(Month)

    Month = calendar.month_name[Today.month].upper()
    cursor.execute(f"SELECT [Room/Shop ID] FROM [Monthly Report Data] WHERE [For The Month Of] = '{Month}'")
    RawIDs = cursor.fetchall()
    IDs = [str(ID) for ID, in RawIDs]

    if all(ID in IDs for ID in list(Shop_IDs + Room_IDs)):
        DisplayRecords(Month)
        print("\n>>> 'Number Of Days Occupied' UPDATED Successfully <<<\n")

    elif any(ID in IDs for ID in list(Shop_IDs + Room_IDs)):
        print('\n', '-' * 75, sep='')
        print('Some Records Are MISSING, Check Your Database And TRY AGAIN...')
        print('-' * 75, '\n', sep='')

    else:
        print('\n', '-' * 75, sep='')
        print('NO Records FOUND To Update, Check Your Database And TRY AGAIN...')
        print('-' * 75, '\n', sep='')

def Update_ToDate_Field():
    Date = GetDate("'To (Date)'")[0]
    ID = GetDetails('Vacating Room/Shop ID', PossibleValues= list(Shop_IDs + Room_IDs))

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
        if RawData in ['', 'NONE']:
            VacatingTenant_List = TenantIDs if RawData == '' else []
            break
        else:
            IsRunning, VacatingTenant_List = GenerateList('Vacating Tenant ID(s) (eg. 0033, 0044)', RawData)
            if not IsRunning:
                if (all(TenantID.isdigit() for TenantID in VacatingTenant_List) and
                    all("{:04d}".format(int(TenantID)) in TenantIDs for TenantID in VacatingTenant_List)):
                        VacatingTenant_List = ["{:04d}".format(int(TenantID)) for TenantID in VacatingTenant_List]
                        break
                else:
                    print('INVALID Tenant ID, TRY AGAIN...')

    print()
    for TenantID in VacatingTenant_List:
        cursor.execute(f"UPDATE [Occupancy Information] SET [To (Date)] = ? WHERE [Room/Shop ID] = '{ID}' AND [Tenant ID] = '{TenantID}';", (Date,))
        cursor.commit()
    return VacatingTenant_List, Date

# OTHER FUNCTIONS
def Get_DateTime(Month = None):
    Year = Today.strftime('%Y')
    if Month == None:
        while True:
            Month = input('\nEnter The Desired Month (eg. JAN or JANUARY): ').upper()
            Month = calendar.month_name[Today.month-1].upper() if Month == '' else Month
            Month = MonthNames[Month] if Month in MonthNames.keys() else Month
            Month = Month if Month in MonthNames.values() else Month
            if Month is None:
                print('INVALID Month Name, TRY AGAIN...')
                continue
            break
    PenultimateMonth = calendar.month_name[Today.month-1].upper()
    PreviousMonth = list(MonthNames.values())[(list(MonthNames.values()).index(Month))-1]
    return PenultimateMonth, Month, PreviousMonth, Year

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
        if ANS in YES:
            return True
        elif ANS in NO:
            return False
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
