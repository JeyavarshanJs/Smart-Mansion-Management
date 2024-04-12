import datetime, calendar

from CustomModules.VariablesModule import *
from CustomModules.EstablishConnection import *

def DuplicateRecords_MonthlyReportData():
    Today = datetime.date.today()
    Month = calendar.month_name[Today.month].upper()
    PreviousMonth = list(MonthNames.values())[(list(MonthNames.values()).index(Month))-1]

    while True:
        Date = input('\nEnter The Desired Date (DD/MM/YYYY): ').upper()
        Date = Today.strftime(r'%d/%m/%Y').upper() if Date == '' else Date

        try:
            Date = datetime.datetime.strptime(Date, r'%d/%m/%Y')
            Date = datetime.date.strftime(Date, r'%Y-%m-%d')
            break
        except:            
            print('INVALID Date, TRY AGAIN...')
            continue

    cursor.execute(f"SELECT [Room/Shop ID], [Closing Sub-Meter Reading] FROM [Monthly Report Data] WHERE [For The Month Of] = '{PreviousMonth}';")
    Records = cursor.fetchall()
    
    for Record in Records:
        ID = Record[0]
        
        cursor.execute(f"SELECT [Closing Sub-Meter Reading], [Closing Date] FROM [Unusual Departure Details] WHERE [For The Month Of] = '{Month}' AND [Room/Shop ID] = '{ID}';")
        RawRecords = cursor.fetchall()
        if len(RawRecords) == 0:
            OpeningReading = Record[1]
        elif len(RawRecords) == 1:
            OpeningReading = RawRecords[0][0]
        else:
            DateOBJs = [datetime.datetime.strptime(str(Record[1])[:10], r'%Y-%m-%d') for Record in RawRecords]
            MaxDate = max(DateOBJs)

            OpeningReading = None
            for Record in RawRecords:
                OpeningReading = Record[0] if MaxDate == datetime.datetime.strptime(str(Record[1])[:10], r'%Y-%m-%d') else OpeningReading

        cursor.execute(f"INSERT INTO [Monthly Report Data] ([Room/Shop ID], [Opening Sub-Meter Reading], [Closing Date], [For The Month Of]) \
                       VALUES (?, ?, ?, ?);", (ID, OpeningReading, Date, Month))
        cursor.commit() 

    print(f"Records Duplicated in the Table ({SUB_MENU_DUPLICATE_RECORDS[1]}) SUCCESSFULLY...")        

def DuplicateRecords_DUEDetails():
    Today = datetime.date.today()
    Month = calendar.month_name[Today.month-1].upper()
    Year = Today.strftime(r'%Y')
    
    cursor.execute(f"SELECT TI.ID, TI.[Full Name], OI.[Room/Shop ID] FROM [Tenant's Information] as TI INNER JOIN [Occupancy Information] as OI \
                   ON TI.ID = OI.[Tenant ID];")
    Records = cursor.fetchall()

    for Record in Records:
        TenantID = Record[0]
        FullName = Record[1]
        ID = Record[2]
        cursor.execute(f"INSERT INTO [DUE Details] VALUES ('{TenantID}', '{FullName}', '{ID}', 0, '{Month}', '{Year}');")
        cursor.commit()     

    print(f"Records Duplicated in the Table ({SUB_MENU_DUPLICATE_RECORDS[2]}) SUCCESSFULLY...")        

def DuplicateRecords_PaymentDetails():
    Today = datetime.date.today()
    Month = calendar.month_name[Today.month-1].upper()
    Year = Today.strftime(r'%Y')

    cursor.execute("SELECT MAX([Receipt Number]) FROM [Payment Details]")
    ReceiptNumber_S = int(cursor.fetchone()[0])
    cursor.execute("SELECT MAX([Receipt Number]) FROM [Payment Details (NS)]")
    ReceiptNumber_NS = int(cursor.fetchone()[0])
    ReceiptNumber = max(ReceiptNumber_S, ReceiptNumber_NS)

    for ID in sorted(Shop_IDs + Room_IDs):
        cursor.execute(f"SELECT [Tenant ID], [Tenant Name] FROM [Occupancy Information] WHERE [Room/Shop ID] = '{ID}' AND [To (Date)] IS NULL \
                        AND [Tenant ID] IS NOT NULL")
        Records = cursor.fetchall()
        if Records != []:
            for Record in Records:
                cursor.execute(f"INSERT INTO [Payment Details] VALUES ({ReceiptNumber}, '{Record[0]}', '{Record[1]}', '{ID}', NULL, 'UNPAID', NULL, '{Month}', '{Year}');")
                cursor.commit()     
                ReceiptNumber += 1

    print(f"Records Duplicated in the Table ({SUB_MENU_DUPLICATE_RECORDS[3]}) SUCCESSFULLY...")        
