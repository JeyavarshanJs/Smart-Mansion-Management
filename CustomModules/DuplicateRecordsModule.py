import datetime, calendar, winsound

from CustomModules.VariablesModule import *
from CustomModules.EstablishConnection import *

Today = datetime.date.today()
Year = Today.strftime('%Y')


def DuplicateRecords_MonthlyReportData():
    Month = calendar.month_name[Today.month].upper()
    PreviousMonth = calendar.month_name[Today.month-1].upper()

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

    cursor.execute(f"SELECT [Room/Shop ID], [Closing Sub-Meter Reading] FROM [Monthly Report Data] WHERE [For The Month Of] = '{PreviousMonth}' AND [Year (YYYY)] = '{Year}';")
    Records = cursor.fetchall()

    for Record in Records:
        ID = Record[0]
        cursor.execute(f"SELECT [Closing Sub-Meter Reading], [Closing Date] FROM [Unusual Occupancy Details] WHERE [For The Month Of] = '{Month}' \
                         AND [Year (YYYY)] = '{Year}' AND [Room/Shop ID] = '{ID}';")
        UODRecords = cursor.fetchall()
        if len(UODRecords) in [0, 1]:
            OpeningReading = Record[1] if len(UODRecords) == 0 else UODRecords[0][0]
        else:
            DateOBJs = [datetime.datetime.strptime(str(Record[1])[:10], r'%Y-%m-%d') for Record in UODRecords]
            MaxDate = max(DateOBJs)

            OpeningReading, = (Record[0] for Record in UODRecords if MaxDate == datetime.datetime.strptime(str(Record[1])[:10], r'%Y-%m-%d'))

        cursor.execute(f"INSERT INTO [Monthly Report Data] ([Room/Shop ID], [Opening Sub-Meter Reading], [Closing Date], [For The Month Of], [Year (YYYY)]) \
                       VALUES (?, ?, ?, ?, ?);", (ID, OpeningReading, Date, Month, Year))
        cursor.commit() 

    print(">> Records Duplicated in the Table (Monthly Report Data) SUCCESSFULLY <<")        
    winsound.Beep(1000, 500)

def DuplicateRecords_DUEDetails():
    Month = calendar.month_name[Today.month-1].upper()

    cursor.execute(f"""
                     SELECT TI.[ID], TI.[Full Name], OI.[Room/Shop ID] FROM [Tenant's Information] TI 
                     INNER JOIN [Occupancy Information] OI ON TI.ID = OI.[Tenant ID]
                     WHERE OI.[To (Date)] IS NULL;
    """)
    Records = cursor.fetchall()

    for Record in Records:
        TenantID, FullName, ID = Record
        cursor.execute(f"INSERT INTO [DUE Details] VALUES ('{TenantID}', '{FullName}', '{ID}', 0, '{Month}', '{Year}');")
        cursor.commit()     

    print(">> Records Duplicated in the Table (DUE Details) SUCCESSFULLY <<")
    winsound.Beep(1000, 500)

def DuplicateRecords_PaymentDetails():
    def GetReceiptNumber(Table):
        cursor.execute(f"SELECT MAX([Receipt Number]) FROM [{Table}] WHERE [Year (YYYY)] = '{Year}';")
        RawData, = cursor.fetchone()
        return int(RawData) if RawData is not None else 0

    Month = calendar.month_name[Today.month-1].upper()
    ReceiptNumber = max(GetReceiptNumber('Payment Details'), GetReceiptNumber('Payment Details (NS)')) + 1

    for ID in sorted(Shop_IDs + Room_IDs):
        cursor.execute(f"SELECT [Tenant ID], [Tenant Name] FROM [Occupancy Information] WHERE [Room/Shop ID] = '{ID}' AND [To (Date)] IS NULL;")
        Records = cursor.fetchall()
        if Records != []:
            for Record in Records:
                cursor.execute(f"INSERT INTO [Payment Details] VALUES ({ReceiptNumber}, '{Record[0]}', '{Record[1]}', '{ID}', NULL, 'UNPAID', NULL, '{Month}', '{Year}');")
                cursor.commit()     
                ReceiptNumber += 1

    print(">> Records Duplicated in the Table (Payment Details) SUCCESSFULLY <<")        
    winsound.Beep(1000, 500)
