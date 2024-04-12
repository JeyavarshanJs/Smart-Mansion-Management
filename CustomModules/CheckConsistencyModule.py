import datetime, calendar

from CustomModules.VariablesModule import *
from CustomModules.EstablishConnection import *


def CheckConsistency_ReceiptNumber():
    cursor.execute("SELECT DISTINCT [Year (YYYY)] FROM [Payment Details]")
    a = len(cursor.fetchall())
    cursor.execute("SELECT MAX([Receipt Number]) FROM [Payment Details]")
    MAX_VAL = int(cursor.fetchone()[0])
    MissingNumbers = []
    for i in range(1, MAX_VAL+1):
        cursor.execute(f"SELECT [Tenant ID] FROM [Payment Details] WHERE [Receipt Number] = ?;", (i,))
        b = cursor.fetchone()
        b = len(b) if b != None else b
        if b == None or b < a:
            MissingNumbers.append(i)
    print('\nMissing Receipt Number Are As Follows,\n  ', end='')
    for i in MissingNumbers:
        if i == MissingNumbers[-1]:
            print(i)
        else:
            print(i, end=', ')

def CheckConsistency_ID():
    Today = datetime.date.today()
    Month = calendar.month_name[Today.month].upper()

    cursor.execute(f"SELECT [Tenant ID], [Room/Shop ID] FROM [Payment Details] WHERE [For The Month Of] = '{Month}'")
    Records = cursor.fetchall()
    for Record in Records:
        TenantID = Record[0]
        ID = Record[1]
        cursor.execute(f"SELECT * FROM [Occupancy Information] WHERE [Tenant ID] = '{TenantID}' \
                       AND [Room/Shop ID] = '{ID}' AND [To (Date)] IS NULL")
        a = cursor.fetchall()
        a = len(a) if a != None else 0
        cursor.execute(f"SELECT * FROM [DUE Details] WHERE [Tenant ID] = '{TenantID}' AND [Room/Shop ID] = '{ID}' \
                       AND [For The Month Of] = '{Month}'")
        b = cursor.fetchall()
        b = len(b) if b != None else 0
        if a != 1 or b != 1:
            print(f"\nRoom/Shop ID: {ID} is INCONSISTENT...")
