import math, datetime, calendar
from prettytable import PrettyTable

from CustomModules.VariablesModule import *
from CustomModules.EstablishConnection import *

def InsertData_WaterPurchaseDetails():
    Today = datetime.date.today()
    Month = calendar.month_name[Today.month].upper()

    while True:
        Date = input('\nEnter The Desired Date (DD/MM/YYYY): ').upper()
        Date = Today.strftime(r'%d/%m/%Y').upper() if Date == '' else Date

        try:
            Date = datetime.datetime.strptime(Date, r'%d/%m/%Y')
            Date = datetime.date.strftime(Date, r'%Y-%m-%d')
            break
        except Exception:
            print('INVALID Date, TRY AGAIN...')
            continue

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
    Today = datetime.date.today()
    Month = calendar.month_name[Today.month].upper()
    PreviousMonth = list(MonthNames.values())[(list(MonthNames.values()).index(Month))-1]
    VacatingTenant_List = []

    # DATE
    while True:
        Date = input('\nEnter The Desired Closing Date (DD/MM/YYYY): ').strip()
        Date = Today.strftime(r'%d/%m/%Y') if Date == '' else Date

        try:
            DateOBJ = datetime.datetime.strptime(Date, r'%d/%m/%Y')
            Date = datetime.date.strftime(DateOBJ, r'%Y-%m-%d')
            break
        except Exception:            
            print('INVALID Date, TRY AGAIN...')
            continue

    # ROOM/SHOP ID & TENANT VACATING
    IsRunning = True
    while IsRunning:
        while True:
            ID = input('\nEnter Room/Shop ID: ').strip().upper()
            if ID in list(Shop_IDs + Room_IDs):
                break
            else:
                print('INVALID Room/Shop ID, TRY AGAIN...')

        cursor.execute(f"SELECT [Tenant ID], [Tenant Name] FROM [Occupancy Information] WHERE [Room/Shop ID] = '{ID}'")
        Records = cursor.fetchall()
        TenantIDs = [Record[0] for Record in Records]

        Table = PrettyTable()
        Table.field_names = ['Tenant ID', 'Tenant Name']
        Table.align['Tenant Name'] = 'l'
        Table.add_rows(Records)
        print('\n', Table, sep='')

        print()
        while True:
            print("\n----ENTER '' IF EVERYONE IS VACATING----")
            RawData = input('Enter The Vacating Tenant ID(s) (eg. 0033, 0044): ').strip()
            if RawData == '':
                VacatingTenant_List = TenantIDs
                IsRunning = False
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
                    IsRunning = False
                    break

    # NUMBER OF DAYS OCCUPIED
    while True:
        DaysOccupied = input('\nEnter Number Of Days Occupied: ').strip()
        if DaysOccupied in [str(_) for _ in range(31)]:
            DaysOccupied = int(DaysOccupied)
            break
        elif DaysOccupied == '':
            DaysOccupied = 15
            break
        else:
            print("INVALID Entry, TRY AGAIN...")

    # CLOSING READING
    while True:
        ClosingReading = input(f"\nEnter 'Closing Sub-Meter Reading' For The Room/Shop (ID: {ID}): ").strip()
        try:
            ClosingReading = round(float(ClosingReading), 1)
            break
        except ValueError:
            print("INVALID 'Closing Sub-Meter Reading', TRY AGAIN...")

    # OPENING READING
    cursor.execute(f"SELECT [Closing Sub-Meter Reading], [Closing Date] FROM [Unusual Departure Details] WHERE [For The Month Of] = '{Month}' AND [Room/Shop ID] = '{ID}';")
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
    while True:
        UserPreference = input('\nDo You Want To Edit This Record? (Y/N): ').strip().upper()
        if UserPreference == 'Y':
            print()
            return InsertData_UnusualDepartureDetails()
        elif UserPreference in ['N', '']:
            break
        else:
            print('INVALID Choice, TRY AGAIN...')

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

    cursor.execute("INSERT INTO [Unusual Departure Details] VALUES (?, ?, ?, ?, ?, ?, ?);", (ID, DaysOccupied, ClosingReading, OpeningReading, Date, Month, TotalRent))
    cursor.commit()
    return ID, Date, VacatingTenant_List

def InsertData_PaymentDetailsNS(ID = None, VacatingTenant_List = None, Date = None):
    Today = datetime.date.today()
    Month = calendar.month_name[Today.month].upper()
    PreviousMonth = list(MonthNames.values())[(list(MonthNames.values()).index(Month))-1]
    Year = Today.strftime(r'%Y')

    cursor.execute("SELECT MAX([Receipt Number]) FROM [Payment Details]")
    RawReceiptNumber_S = cursor.fetchone()
    ReceiptNumber_S = int(RawReceiptNumber_S[0]) if RawReceiptNumber_S[0] != None else 0

    cursor.execute("SELECT MAX([Receipt Number]) FROM [Payment Details (NS)]")
    RawReceiptNumber_NS = cursor.fetchone()
    ReceiptNumber_NS = int(RawReceiptNumber_NS[0]) if RawReceiptNumber_NS[0] != None else 0

    ReceiptNumber = max(ReceiptNumber_S, ReceiptNumber_NS) + 1

    if ID == None:
        # ROOM/SHOP ID
        while True:
            ID = input('\nEnter Room/Shop ID: ').strip().upper()
            if ID in list(Shop_IDs + Room_IDs):
                break
            else:
                print('INVALID Room/Shop ID, TRY AGAIN...')

    if VacatingTenant_List == None:
        cursor.execute(f"SELECT [Tenant ID] FROM [Occupancy Information] WHERE [Room/Shop ID] = '{ID}'")
        Records = cursor.fetchall()
        TenantIDs = [Record[0] for Record in Records]

        while True:
            print("\n\n----ENTER '' IF EVERYONE IS VACATING----")
            RawData = input('Enter The Vacating Tenant ID(s) (eg. 0033, 0044): ').strip()
            if RawData == '':
                VacatingTenant_List = TenantIDs
                IsRunning = False
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

        cursor.execute(f"SELECT [Total Rent], [Closing Date] FROM [Unusual Departure Details] WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}'")
        RawRecords = cursor.fetchall()
        if len(RawRecords) == 0:
            print('\n', '-' * 75, sep='')
            print("No Record FOUND, TRY UPDATING 'Unusual Departure Details' Field...")
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
                IndividualRent = math.ceil(TotalRent / TenantCount) + BalanceDue
                cursor.execute(f"INSERT INTO [Payment Details (NS)] VALUES ({ReceiptNumber}, '{TenantID}', '{TenantName}', '{ID}', {IndividualRent}, 'UNPAID', NULL, '{Month}', '{Year}');")
                cursor.commit()

            ReceiptNumber += 1
    return Month, ReceiptNumber_List

