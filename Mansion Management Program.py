import pyodbc
import math, datetime, calendar
import os, sys
from PIL import Image, ImageDraw, ImageFont

# UPDATE
def Update_TenantName_Field(TableName):
    if TableName == SUB_MENU_UPDATE_TenantName[1]:
        cursor.execute("SELECT [Tenant ID] FROM [Occupancy Information] WHERE [Tenant ID] IS NOT NULL;")
        records = cursor.fetchall()
        for record in records:
            ID = record[0]
            cursor.execute(f"SELECT [Full Name] FROM [Tenant's Information] WHERE ID = '{ID}';")
            TenantName = cursor.fetchone()[0] 
            cursor.execute(f"UPDATE [Occupancy Information] SET [Tenant Name] = '{TenantName}' WHERE [Tenant ID] = ?;", (ID,))
            con.commit()
    elif TableName == SUB_MENU_UPDATE_TenantName[2]:
        cursor.execute("SELECT [Tenant ID] FROM [Payment Details] WHERE [Tenant Name] IS NULL;")
        records = cursor.fetchall()
        for record in records:
            ID = record[0]
            cursor.execute(f"SELECT [Full Name] FROM [Tenant's Information] WHERE ID = '{ID}';")
            TenantName = cursor.fetchone()[0]
            cursor.execute(f"UPDATE [Payment Details] SET [Tenant Name] = '{TenantName}' WHERE [Tenant ID] = ?;", (ID,))
            con.commit()
    print("'Tenant Name' UPDATED Successfully...")

def Update_TotalRent_Field():
    Today = datetime.date.today()
    while True:
        Month = input('\nEnter The Desired Month (eg. JAN or JANUARY): ').upper()
        Month = calendar.month_name[Today.month].upper() if Month == '' else Month
        if Month in MonthNames.keys():
            Month = MonthNames[Month]
            break
        elif Month in MonthNames.values():
            break
        else:
            print('INVALID Month Name, TRY AGAIN...')

    cursor.execute("SELECT * FROM [Room/Shop Data] ORDER BY [Room/Shop ID]")
    records = cursor.fetchall()
    for record in records:
        ID = record[0]
        if Month == calendar.month_name[Today.month-1].upper():
            TenantCount = record[1]
        else:
            while True:
                TenantCount = input(f'\nEnter Tenant Count For The Room/Shop (ID: {ID}): ') if ID in Shop_IDs else 1
                if TenantCount.isdigit():
                    TenantCount = int(TenantCount)
                    break
                else:
                    print('INVALID Tenant Count, TRY AGAIN...')

        Room_Rent = record[TenantCount+1] if TenantCount != 0 else 0
        Other_Charges = record[TenantCount+4] if TenantCount != 0 else 0
        Current_Charge = record[8]

        cursor.execute(f"SELECT [Number Of Days Occupied], [Closing Sub-Meter Reading], [Opening Sub-Meter Reading] \
                       FROM [Monthly Report Data] WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
        Data = cursor.fetchone()
        Days_Occupied = Data[0]
        Closing_Reading = Data[1]
        Opening_Reading = Data[2]
        Total_Rent = math.ceil((Room_Rent + Other_Charges)/30 * Days_Occupied + (Closing_Reading - Opening_Reading)*Current_Charge) \
                                if (Room_Rent + Other_Charges) != 0 else 0
        cursor.execute(f"UPDATE [Monthly Report Data] SET [Total Rent] = ? WHERE [Room/Shop ID] = ? AND \
                       [For The Month Of] = '{Month}';", (Total_Rent, ID))
        con.commit()
    print("'Total Rent' UPDATED Successfully...")

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

    cursor.execute(f"SELECT [Tenant ID], [Room/Shop ID] FROM [Payment Details] WHERE [For The Month Of] = '{Month}';")
    records = cursor.fetchall()
    for record in records:
        TenantID = record[0]        
        ID = record[1]

        cursor.execute(f"SELECT [Total Rent] FROM [Monthly Report Data] WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
        TotalRent = cursor.fetchone()[0]

        # Tenant Count
        if Month == calendar.month_name[Today.month-1].upper():
            cursor.execute(f"SELECT [Tenant Count] FROM [Room/Shop Data] WHERE [Room/Shop ID] = '{ID}';")
            TenantCount = cursor.fetchone()[0]
        else:
            while True:
                TenantCount = input(f'\nEnter Tenant Count For The Room/Shop (ID: {ID}): ') if ID in Shop_IDs else 1
                if TenantCount.isdigit() and int(TenantCount) in [1, 2, 3]:
                    TenantCount = int(TenantCount)
                    break
                else:
                    print('INVALID Tenant Count, TRY AGAIN...')

        cursor.execute(f"SELECT [DUE Amount] FROM [DUE Details] WHERE [Tenant ID] = '{TenantID}' AND [For The Month Of] = '{Month}';")
        BalanceDue = cursor.fetchone()[0]

        IndividualRent = math.ceil(TotalRent / TenantCount) + int(BalanceDue)

        cursor.execute(f"UPDATE [Payment Details] SET [Individual Rent] = '{IndividualRent}' WHERE [Tenant ID] = ? AND [Room/Shop ID] = '{ID}' AND \
                       [For The Month Of] = '{Month}';", (TenantID,))
        con.commit()
    print("'Individual Rent' UPDATED Successfully...")

def Update_TenantsCount_Field():
    cursor.execute('UPDATE [Room/Shop Data] SET [Tenant Count] = 0;')
    con.commit()
    cursor.execute("SELECT [Room/Shop ID], COUNT(*) FROM [Occupancy Information] WHERE [To (Date)] IS NULL GROUP BY [Room/Shop ID];")
    records = cursor.fetchall()
    for record in records:
        ID = record[0]
        Tenant_Count = record[1]
        cursor.execute('UPDATE [Room/Shop Data] SET [Tenant Count] = ? WHERE [Room/Shop ID] = ?;', (Tenant_Count, ID))
        con.commit()
    print("'Tenant Count' UPDATED Successfully...")

def Update_CurrentStatus_Field():
    cursor.execute("SELECT [Tenant ID] FROM [Occupancy Information] WHERE [To (Date)] IS NOT NULL;")
    TenantIDs = cursor.fetchall()
    for TenantID in TenantIDs:
        cursor.execute(f"UPDATE [Tenant's Information] SET [Current Status] = 'VACATED' WHERE [ID] = '{TenantID[0]}'")
        cursor.commit()
    print("'Current Status' UPDATED Successfully...")

# GENERATE RENT RECEIPT
def GenerateRoomRentReceipt_ALL():
    Today = datetime.date.today()
    DatePreference = ''    
    while True:
        Month = input('\nEnter The Desired Month (eg. JAN or JANUARY): ').upper()
        if DatePreference == '':
            DatePreference = 'With Month' if Month.upper() == 'WITH MONTH' else ''
        Month = calendar.month_name[Today.month-1].upper() if Month == '' else Month
        if Month in MonthNames.keys():
            Month = MonthNames[Month]
            break
        elif Month in MonthNames.values():
            break
        elif DatePreference != '':
            print('Preference ACCEPTED...')
        else:            
            print('INVALID Month Name, TRY AGAIN...')

    Date = Today.strftime(r'%d/%m/%Y')
    cursor.execute(f"SELECT [Tenant ID], [Individual Rent], [Year (YYYY)], [Receipt Number], [Tenant Name], [Room/Shop ID] \
                   FROM [Payment Details] WHERE [Status] = 'UNPAID' AND [For The Month Of] = '{Month}';")
    records = cursor.fetchall()
    for record in records:
        TenantID = record[0]
        FinalAmount= int(record[1])
        Year = record[2]
        ReceiptNumber = record[3]
        TenantName = record[4]
        ID = record[5]

        if ID not in Room_IDs:
            print('\n', '-' * 50)
            print(f"'{ID}' Is not a ROOM, So Receipt Generation SKIPPED...")
            print('-' * 50, '\n')
            continue

        cursor.execute(f"SELECT [Tenant Count], [Rent-1], [Rent-2], [Rent-3] FROM [Room/Shop Data] WHERE [Room/Shop ID] = '{ID}'")
        Datas = cursor.fetchone()
        # Tenant Count
        if Month == calendar.month_name[Today.month-1].upper():
            TenantCount = Datas[0]
        else:
            while True:
                TenantCount = input(f'\nEnter Tenant Count For The Room/Shop (ID: {ID}): ')
                if TenantCount.isdigit() and int(TenantCount) in [1, 2, 3]:
                    TenantCount = int(TenantCount)
                    break
                else:
                    print('INVALID Tenant Count, TRY AGAIN...')
        Room_Rent = math.ceil((Datas[TenantCount])/TenantCount) if TenantCount != 0 else 0

        cursor.execute(f"SELECT [DUE Amount] FROM [DUE Details] WHERE [Tenant ID] = '{TenantID}' AND [Room/Shop ID] = '{ID}' \
                       AND [For The Month Of] = '{Month}';")
        BalanceDue = cursor.fetchone()[0]

        cursor.execute(f"SELECT [Number Of Days Occupied], [Closing Sub-Meter Reading], [Opening Sub-Meter Reading] \
                       FROM [Monthly report Data] WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
        Datas = cursor.fetchone()
        Days_Occupied = Datas[0]
        Room_Rent = math.ceil((Room_Rent * Days_Occupied)/30)
        UtilityCharges = FinalAmount - Room_Rent - int(BalanceDue)
        ClosingReading = Datas[1]
        OpeningReading = Datas[2]
        UnitsConsumed = ClosingReading - OpeningReading
        
        if DatePreference == 'Without Month':
            Date = Date[-5:]
        else:
            Date = Date[-8:]
    
        # Generating Rent Receipt-1
        Template = Image.open('Room Rent Receipt-1.jpg', mode='r')

        Description_Size, Description_Colour = 50, (0, 0, 0)
        Description_Font = ImageFont.truetype('CalibriFont Regular.ttf', Description_Size)
        Data_Size, Data_Colour = 45, (0, 0, 0)
        Data_Font = ImageFont.truetype('CalibriFont Regular.ttf', Data_Size)
        FinalAmount_Size, FinalAmount_Colour = 50, (0, 0, 0)
        FinalAmount_Font = ImageFont.truetype('CalibriFont Bold.ttf', FinalAmount_Size)
        ReceiptNumber_Size, ReceiptNumber_Colour = 45, (0, 0, 0)
        ReceiptNumber_Font = ImageFont.truetype('CalibriFont Bold.ttf', ReceiptNumber_Size)

        Draw = ImageDraw.Draw(Template)
        FinalAmountText_Width = Draw.textlength(str(FinalAmount), font=Description_Font)
        RoomIDText_Width = Draw.textlength(ID, font=Description_Font)
        Date_Width = Draw.textlength(Date, Data_Font)

        FinalAmount_Position1 = (459 + (126 - FinalAmountText_Width), 554)
        RoomID_Position = (925 + (73 - RoomIDText_Width), 554)
        MonthAndTenantName_Position = (291, 620)
        ClosingReading_Position = (675, 729)
        OpeningReading_Position = (675, 793)
        UnitsConsumed_Position = (675, 856)
        RoomRent_Position = (675, 920)
        UtilityCharges_Position = (675, 981)        
        FinalAmount_Position2 = (675, 1045)
        ReceiptNumber_Position = (337, 327)
        Date_Position = (913 + (217 - Date_Width), 327)

        Draw.text(FinalAmount_Position1, str(FinalAmount), Description_Colour, Description_Font)
        Draw.text(RoomID_Position, ID, Description_Colour, Description_Font)
        Draw.text(MonthAndTenantName_Position, f"{Month.capitalize()}-{Year[-2:]} From {TenantName}.", Description_Colour, Description_Font)
        Draw.text(ClosingReading_Position, str(ClosingReading), Data_Colour, Data_Font)
        Draw.text(OpeningReading_Position, str(OpeningReading), Data_Colour, Data_Font)
        Draw.text(UnitsConsumed_Position, str(UnitsConsumed), Data_Colour, Data_Font)
        Draw.text(RoomRent_Position, str(Room_Rent), Data_Colour, Data_Font)
        Draw.text(UtilityCharges_Position, str(UtilityCharges), Data_Colour, Data_Font)
        Draw.text(FinalAmount_Position2, str(FinalAmount), FinalAmount_Colour, FinalAmount_Font)
        Draw.text(ReceiptNumber_Position, str(ReceiptNumber), ReceiptNumber_Colour, ReceiptNumber_Font)
        Draw.text(Date_Position, Date, Data_Colour, Data_Font)

        Template.save(rf'Rent Receipts\Room Rent Receipt No-{ReceiptNumber}_1.jpg', dpi = (300, 300))

        # Generating Rent Receipt-2
        Template = Image.open('Room Rent Receipt-2.jpg', mode='r')

        Description_Size, Description_Colour = 42, (0, 0, 0)
        Description_Font = ImageFont.truetype('CalibriFont Regular.ttf', Description_Size)
        ReceiptNumber_Size, ReceiptNumber_Colour = 38, (0, 0, 0)
        ReceiptNumber_Font = ImageFont.truetype('CalibriFont Bold.ttf', ReceiptNumber_Size)
        Date_Size, Date_Colour = 38, (0, 0, 0)
        Date_Font = ImageFont.truetype('CalibriFont Regular.ttf', Date_Size)

        Draw = ImageDraw.Draw(Template)
        FinalAmountText_Width = Draw.textlength(str(FinalAmount), font=Description_Font)
        RoomIDText_Width = Draw.textlength(ID, font=Description_Font)
        Date_Width = Draw.textlength(Date, Date_Font)

        FinalAmount_Position = (396 + (105 - FinalAmountText_Width), 476)
        RoomID_Position = (786 + (60 - RoomIDText_Width), 476)
        MonthAndTenantName_Position = (89, 530)
        ReceiptNumber_Position = (292, 299)
        Date_Position = (953 + (199 - Date_Width), 299)

        Draw.text(FinalAmount_Position, str(FinalAmount), Description_Colour, Description_Font)
        Draw.text(RoomID_Position, ID, Description_Colour, Description_Font)
        Draw.text(MonthAndTenantName_Position, f"{Month.capitalize()}, {Year} From {TenantName}.", Description_Colour, Description_Font)
        Draw.text(ReceiptNumber_Position, str(ReceiptNumber), ReceiptNumber_Colour, ReceiptNumber_Font)
        Draw.text(Date_Position, Date, Date_Colour, Date_Font)

        Template.save(rf'Rent Receipts\Room Rent Receipt No-{ReceiptNumber}_2.jpg', dpi = (300, 300))
        print(f"Rent Receipts generated for '{TenantName}'.")

def GenerateRoomRentReceipt_SPECIFIC():
    Today = datetime.date.today() 
    DatePreference = ''    
    while True:
        Month = input('\nEnter The Desired Month (eg. JAN or JANUARY): ').upper()
        if DatePreference == '':
            DatePreference = 'Without Date' if Month.upper() == 'WITHOUT DATE' else 'Without Month' \
                                            if Month.upper() == 'WITHOUT MONTH' else ''
        Month = calendar.month_name[Today.month-1].upper() if Month == '' else Month
        if Month in MonthNames.keys():
            Month = MonthNames[Month]
            break
        elif Month in MonthNames.values():
            break
        elif DatePreference != '':
            print('Preference ACCEPTED...')
        else:            
            print('INVALID Month Name, TRY AGAIN...')

    while True:
        ReceiptNOs = input('\nEnter The Receipt NOs (eg. 11-22, 33): ')
        a = ReceiptNOs.split(',')
        for i in range(len(a)):
            a[i] = a[i].strip()

        ReceiptNumber_List = []
        for i in a:
            if '-' in i:
                StartID, EndID = i.split('-')
                if StartID.strip().isdigit() and EndID.strip().isdigit():
                    StartID, EndID = int(StartID.strip()), int(EndID.strip())
                else:
                    print('INVALID Receipt Numbers, TRY AGAING...')
                    continue
                ReceiptNumber_List.extend([_ for _ in range(StartID, EndID+1)])
            else:
                if i.isdigit():
                    ReceiptNumber_List.append(int(i))
                else:
                    print('INVALID Receipt Numbers, TRY AGAING...')
                    continue
        x = 0
        for i in ReceiptNumber_List:
            cursor.execute(f"SELECT [Tenant Name], [Room/Shop ID] FROM [Payment Details] \
                           WHERE [Receipt Number] = {i} AND [Status] = 'UNPAID' AND [For The Month OF] = '{Month}';")
            x += 1 if cursor.fetchone() != None else 0

        if len(ReceiptNumber_List) != x:
            print('Some Tenant ID Are NOT VALID, Try Again...')            
        else:
            break

    Date = Today.strftime(r'%d/%m/%Y')
    for ReceiptNumber in ReceiptNumber_List:
        cursor.execute(f"SELECT [Individual Rent], [Year (YYYY)], [Tenant ID], [Tenant Name], [Room/Shop ID] FROM [Payment Details] \
                       WHERE [Receipt Number] = {ReceiptNumber};")
        record = cursor.fetchone()
        FinalAmount= int(record[0])
        Year = record[1]
        TenantID = record[2]
        TenantName = record[3]
        ID = record[4]

        if ID not in Room_IDs:
            print('\n', '-' * 50)
            print(f"'{ID}' Is not a ROOM, So Receipt Generation SKIPPED...")
            print('-' * 50, '\n')
            continue

        cursor.execute(f"SELECT [Tenant Count], [Rent-1], [Rent-2], [Rent-3] FROM [Room/Shop Data] WHERE [Room/Shop ID] = '{ID}'")
        Datas = cursor.fetchone()
        # Tenant Count
        if Month == calendar.month_name[Today.month-1].upper():
            TenantCount = Datas[0]
        else:
            while True:
                TenantCount = input(f'\nEnter Tenant Count For The Room/Shop (ID: {ID}): ')
                if TenantCount.isdigit() and int(TenantCount) in [1, 2, 3]:
                    TenantCount = int(TenantCount)
                    break
                else:
                    print('INVALID Tenant Count, TRY AGAIN...')
        Room_Rent = math.ceil((Datas[TenantCount])/TenantCount) if TenantCount != 0 else 0

        cursor.execute(f"SELECT [DUE Amount] FROM [DUE Details] WHERE [Tenant ID] = '{TenantID}' AND [Room/Shop ID] = '{ID}' \
                       AND [For The Month Of] = '{Month}';")
        BalanceDue = cursor.fetchone()[0]

        cursor.execute(f"SELECT [Number Of Days Occupied], [Closing Sub-Meter Reading], [Opening Sub-Meter Reading] \
                        FROM [Monthly report Data] WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
        Datas = cursor.fetchone()
        Days_Occupied = Datas[0]
        Room_Rent = math.ceil((Room_Rent * Days_Occupied)/30)
        UtilityCharges = FinalAmount - Room_Rent - int(BalanceDue)
        ClosingReading = Datas[1]
        OpeningReading = Datas[2]
        UnitsConsumed = ClosingReading - OpeningReading        

        if DatePreference == 'Without Date':
            Date = Date[-8:]
        elif DatePreference == 'Without Month':
            Date = Date[-5:]

        # Generating Rent Receipt-1
        Template = Image.open('Room Rent Receipt-1.jpg', mode='r')

        Description_Size, Description_Colour = 50, (0, 0, 0)
        Description_Font = ImageFont.truetype('CalibriFont Regular.ttf', Description_Size)
        Data_Size, Data_Colour = 45, (0, 0, 0)
        Data_Font = ImageFont.truetype('CalibriFont Regular.ttf', Data_Size)
        FinalAmount_Size, FinalAmount_Colour = 50, (0, 0, 0)
        FinalAmount_Font = ImageFont.truetype('CalibriFont Bold.ttf', FinalAmount_Size)
        ReceiptNumber_Size, ReceiptNumber_Colour = 45, (0, 0, 0)
        ReceiptNumber_Font = ImageFont.truetype('CalibriFont Bold.ttf', ReceiptNumber_Size)

        Draw = ImageDraw.Draw(Template)
        FinalAmountText_Width = Draw.textlength(str(FinalAmount), font=Description_Font)
        RoomIDText_Width = Draw.textlength(ID, font=Description_Font)
        Date_Width = Draw.textlength(Date, Data_Font)

        FinalAmount_Position1 = (459 + (126 - FinalAmountText_Width), 554)
        RoomID_Position = (925 + (73 - RoomIDText_Width), 554)
        MonthAndTenantName_Position = (291, 620)
        ClosingReading_Position = (675, 729)
        OpeningReading_Position = (675, 793)
        UnitsConsumed_Position = (675, 856)
        RoomRent_Position = (675, 920)
        UtilityCharges_Position = (675, 981)        
        FinalAmount_Position2 = (675, 1045)
        ReceiptNumber_Position = (337, 327)
        Date_Position = (913 + (217 - Date_Width), 327)

        Draw.text(FinalAmount_Position1, str(FinalAmount), Description_Colour, Description_Font)
        Draw.text(RoomID_Position, ID, Description_Colour, Description_Font)
        Draw.text(MonthAndTenantName_Position, f"{Month.capitalize()}-{Year[-2:]} From {TenantName}.", Description_Colour, Description_Font)
        Draw.text(ClosingReading_Position, str(ClosingReading), Data_Colour, Data_Font)
        Draw.text(OpeningReading_Position, str(OpeningReading), Data_Colour, Data_Font)
        Draw.text(UnitsConsumed_Position, str(UnitsConsumed), Data_Colour, Data_Font)
        Draw.text(RoomRent_Position, str(Room_Rent), Data_Colour, Data_Font)
        Draw.text(UtilityCharges_Position, str(UtilityCharges), Data_Colour, Data_Font)
        Draw.text(FinalAmount_Position2, str(FinalAmount), FinalAmount_Colour, FinalAmount_Font)
        Draw.text(ReceiptNumber_Position, str(ReceiptNumber), ReceiptNumber_Colour, ReceiptNumber_Font)
        Draw.text(Date_Position, Date, Data_Colour, Data_Font)

        Template.save(rf'Rent Receipts\Room Rent Receipt No-{ReceiptNumber}_1.jpg', dpi = (300, 300))

        # Generating Rent Receipt-2
        Template = Image.open('Room Rent Receipt-2.jpg', mode='r')

        Description_Size, Description_Colour = 42, (0, 0, 0)
        Description_Font = ImageFont.truetype('CalibriFont Regular.ttf', Description_Size)
        ReceiptNumber_Size, ReceiptNumber_Colour = 38, (0, 0, 0)
        ReceiptNumber_Font = ImageFont.truetype('CalibriFont Bold.ttf', ReceiptNumber_Size)
        Date_Size, Date_Colour = 38, (0, 0, 0)
        Date_Font = ImageFont.truetype('CalibriFont Regular.ttf', Date_Size)

        Draw = ImageDraw.Draw(Template)
        FinalAmountText_Width = Draw.textlength(str(FinalAmount), font=Description_Font)
        RoomIDText_Width = Draw.textlength(ID, font=Description_Font)
        Date_Width = Draw.textlength(Date, Date_Font)

        FinalAmount_Position = (396 + (105 - FinalAmountText_Width), 476)
        RoomID_Position = (786 + (60 - RoomIDText_Width), 476)
        MonthAndTenantName_Position = (89, 530)
        ReceiptNumber_Position = (292, 299)
        Date_Position = (953 + (199 - Date_Width), 299)

        Draw.text(FinalAmount_Position, str(FinalAmount), Description_Colour, Description_Font)
        Draw.text(RoomID_Position, ID, Description_Colour, Description_Font)
        Draw.text(MonthAndTenantName_Position, f"{Month.capitalize()}, {Year} From {TenantName}.", Description_Colour, Description_Font)
        Draw.text(ReceiptNumber_Position, str(ReceiptNumber), ReceiptNumber_Colour, ReceiptNumber_Font)
        Draw.text(Date_Position, Date, Date_Colour, Date_Font)

        Template.save(rf'Rent Receipts\Room Rent Receipt No-{ReceiptNumber}_2.jpg', dpi = (300, 300))
        print(f"Rent Receipts generated for '{TenantName}'.")

def GenerateShopRentReceipt_ALL():
    Today = datetime.date.today()
    DatePreference = ''    
    while True:
        Month = input('\nEnter The Desired Month (eg. JAN or JANUARY): ').upper()
        if DatePreference == '':
            DatePreference = 'With Month' if Month.upper() == 'WITH MONTH' else ''
        Month = calendar.month_name[Today.month-1].upper() if Month == '' else Month
        if Month in MonthNames.keys():
            Month = MonthNames[Month]
            break
        elif Month in MonthNames.values():
            break
        elif DatePreference != '':
            print('Preference ACCEPTED...')
        else:            
            print('INVALID Month Name, TRY AGAIN...')

    Date = Today.strftime(r'%d/%m/%Y')
    cursor.execute(f"SELECT [Tenant ID], [Individual Rent], [Year (YYYY)], [Receipt Number], [Tenant Name], [Room/Shop ID] \
                   FROM [Payment Details] WHERE [Status] = 'UNPAID' AND [For The Month Of] = '{Month}';")
    records = cursor.fetchall()
    for record in records:
        TenantID = record[0]
        FinalAmount= int(record[1])
        Year = record[2]
        ReceiptNumber = record[3]
        TenantName = record[4]
        ID = record[5]

        if ID not in Room_IDs:
            print('\n', '-' * 50)
            print(f"'{ID}' Is not a ROOM, So Receipt Generation SKIPPED...")
            print('-' * 50, '\n')
            continue

        cursor.execute(f"SELECT [Tenant Count], [Rent-1], [Rent-2], [Rent-3] FROM [Room/Shop Data] WHERE [Room/Shop ID] = '{ID}'")
        Datas = cursor.fetchone()
        # Tenant Count
        if Month == calendar.month_name[Today.month-1].upper():
            TenantCount = Datas[0]
        else:
            while True:
                TenantCount = input(f'\nEnter Tenant Count For The Room/Shop (ID: {ID}): ')
                if TenantCount.isdigit() and int(TenantCount) in [1, 2, 3]:
                    TenantCount = int(TenantCount)
                    break
                else:
                    print('INVALID Tenant Count, TRY AGAIN...')
        Room_Rent = math.ceil((Datas[TenantCount])/TenantCount) if TenantCount != 0 else 0

        cursor.execute(f"SELECT [DUE Amount] FROM [DUE Details] WHERE [Tenant ID] = '{TenantID}' AND [Room/Shop ID] = '{ID}' \
                       AND [For The Month Of] = '{Month}';")
        BalanceDue = cursor.fetchone()[0]

        cursor.execute(f"SELECT [Number Of Days Occupied], [Closing Sub-Meter Reading], [Opening Sub-Meter Reading] \
                       FROM [Monthly report Data] WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
        Datas = cursor.fetchone()
        Days_Occupied = Datas[0]
        Room_Rent = math.ceil((Room_Rent * Days_Occupied)/30)
        UtilityCharges = FinalAmount - Room_Rent - int(BalanceDue)
        ClosingReading = Datas[1]
        OpeningReading = Datas[2]
        UnitsConsumed = ClosingReading - OpeningReading
        
        if DatePreference == 'Without Month':
            Date = Date[-5:]
        else:
            Date = Date[-8:]
    
        # Generating Rent Receipt-1
        Template = Image.open('Room Rent Receipt-1.jpg', mode='r')

        Description_Size, Description_Colour = 50, (0, 0, 0)
        Description_Font = ImageFont.truetype('CalibriFont Regular.ttf', Description_Size)
        Data_Size, Data_Colour = 45, (0, 0, 0)
        Data_Font = ImageFont.truetype('CalibriFont Regular.ttf', Data_Size)
        FinalAmount_Size, FinalAmount_Colour = 50, (0, 0, 0)
        FinalAmount_Font = ImageFont.truetype('CalibriFont Bold.ttf', FinalAmount_Size)
        ReceiptNumber_Size, ReceiptNumber_Colour = 45, (0, 0, 0)
        ReceiptNumber_Font = ImageFont.truetype('CalibriFont Bold.ttf', ReceiptNumber_Size)

        Draw = ImageDraw.Draw(Template)
        FinalAmountText_Width = Draw.textlength(str(FinalAmount), font=Description_Font)
        RoomIDText_Width = Draw.textlength(ID, font=Description_Font)
        Date_Width = Draw.textlength(Date, Data_Font)

        FinalAmount_Position1 = (459 + (126 - FinalAmountText_Width), 554)
        RoomID_Position = (925 + (73 - RoomIDText_Width), 554)
        MonthAndTenantName_Position = (291, 620)
        ClosingReading_Position = (675, 729)
        OpeningReading_Position = (675, 793)
        UnitsConsumed_Position = (675, 856)
        RoomRent_Position = (675, 920)
        UtilityCharges_Position = (675, 981)        
        FinalAmount_Position2 = (675, 1045)
        ReceiptNumber_Position = (337, 327)
        Date_Position = (913 + (217 - Date_Width), 327)

        Draw.text(FinalAmount_Position1, str(FinalAmount), Description_Colour, Description_Font)
        Draw.text(RoomID_Position, ID, Description_Colour, Description_Font)
        Draw.text(MonthAndTenantName_Position, f"{Month.capitalize()}-{Year[-2:]} From {TenantName}.", Description_Colour, Description_Font)
        Draw.text(ClosingReading_Position, str(ClosingReading), Data_Colour, Data_Font)
        Draw.text(OpeningReading_Position, str(OpeningReading), Data_Colour, Data_Font)
        Draw.text(UnitsConsumed_Position, str(UnitsConsumed), Data_Colour, Data_Font)
        Draw.text(RoomRent_Position, str(Room_Rent), Data_Colour, Data_Font)
        Draw.text(UtilityCharges_Position, str(UtilityCharges), Data_Colour, Data_Font)
        Draw.text(FinalAmount_Position2, str(FinalAmount), FinalAmount_Colour, FinalAmount_Font)
        Draw.text(ReceiptNumber_Position, str(ReceiptNumber), ReceiptNumber_Colour, ReceiptNumber_Font)
        Draw.text(Date_Position, Date, Data_Colour, Data_Font)

        Template.save(rf'Rent Receipts\Room Rent Receipt No-{ReceiptNumber}_1.jpg', dpi = (300, 300))

        # Generating Rent Receipt-2
        Template = Image.open('Room Rent Receipt-2.jpg', mode='r')

        Description_Size, Description_Colour = 42, (0, 0, 0)
        Description_Font = ImageFont.truetype('CalibriFont Regular.ttf', Description_Size)
        ReceiptNumber_Size, ReceiptNumber_Colour = 38, (0, 0, 0)
        ReceiptNumber_Font = ImageFont.truetype('CalibriFont Bold.ttf', ReceiptNumber_Size)
        Date_Size, Date_Colour = 38, (0, 0, 0)
        Date_Font = ImageFont.truetype('CalibriFont Regular.ttf', Date_Size)

        Draw = ImageDraw.Draw(Template)
        FinalAmountText_Width = Draw.textlength(str(FinalAmount), font=Description_Font)
        RoomIDText_Width = Draw.textlength(ID, font=Description_Font)
        Date_Width = Draw.textlength(Date, Date_Font)

        FinalAmount_Position = (396 + (105 - FinalAmountText_Width), 476)
        RoomID_Position = (786 + (60 - RoomIDText_Width), 476)
        MonthAndTenantName_Position = (89, 530)
        ReceiptNumber_Position = (292, 299)
        Date_Position = (953 + (199 - Date_Width), 299)

        Draw.text(FinalAmount_Position, str(FinalAmount), Description_Colour, Description_Font)
        Draw.text(RoomID_Position, ID, Description_Colour, Description_Font)
        Draw.text(MonthAndTenantName_Position, f"{Month.capitalize()}, {Year} From {TenantName}.", Description_Colour, Description_Font)
        Draw.text(ReceiptNumber_Position, str(ReceiptNumber), ReceiptNumber_Colour, ReceiptNumber_Font)
        Draw.text(Date_Position, Date, Date_Colour, Date_Font)

        Template.save(rf'Rent Receipts\Room Rent Receipt No-{ReceiptNumber}_2.jpg', dpi = (300, 300))
        print(f"Rent Receipts generated for '{TenantName}'.")

def GenerateShopRentReceipt_SPECIFIC():
    pass

# CHECK FOR CONSISTENCY
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

# DUPLICATE RECORDS
def DuplicateRecords_MonthlyReportData():
    Today = datetime.date.today()
    Month = calendar.month_name[Today.month].upper()
    PreviousMonth = list(MonthNames.values())[(list(MonthNames.values()).index(Month))-1]
    
    cursor.execute(f"SELECT [Room/Shop ID], [Closing Sub-Meter Reading] FROM [Monthly Report Data] WHERE [For The Month Of] = '{PreviousMonth}';")
    Records = cursor.fetchall()
    for Record in Records:
        ID = Record[0]
        OpeningReading = Record[1]
        cursor.execute(f"INSERT INTO [Monthly Report Data] ([Room/Shop ID], [Opening Sub-Meter Reading], [For The Month Of]) \
                       VALUES ('{ID}', {OpeningReading}, '{Month}');")
        cursor.commit()     

def DuplicateRecords_DUEDetails():
    Today = datetime.date.today()
    Month = calendar.month_name[Today.month-1].upper()
    
    cursor.execute(f"SELECT TI.ID, TI.[Full Name], OI.[Room/Shop ID] FROM [Tenant's Information] as TI INNER JOIN [Occupancy Information] as OI \
                   ON TI.ID = OI.[Tenant ID];")
    Records = cursor.fetchall()
    Year = Today.strftime(r'%Y')
    for Record in Records:
        TenantID = Record[0]
        FullName = Record[1]
        ID = Record[2]
        cursor.execute(f"INSERT INTO [DUE Details] VALUES ('{TenantID}', '{FullName}', '{ID}', 0, '{Month}', '{Year}');")
        cursor.commit()     


# Establish Connection
try:
    con = pyodbc.connect(r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=D:\Python Projects\Smart Mansion Management\Database (MS Access).accdb;')
except:
    print('Database Connection FAILED') 

# Create a Cursor
cursor = con.cursor()

# Global Variables
MonthNames = {'JAN': 'JANUARY', 'FEB': 'FEBRUARY', 'MAR': 'MARCH', 'APR': 'APRIL', 'MAY': 'MAY', 'JUN': 'JUNE', 'JUL': 'JULY', 'AUG': 'AUGUST', 'SEP': 'SEPTEMBER', 'OCT': 'OCTOBER', 'NOV': 'NOVEMBER', 'DEC': 'DECEMBER'}
Room_IDs = ['202', '203', '204', '205', '206', '207', '208', '301', '302', '303', '304', '305', '306', '307', '308', 'S2', 'S3']
Shop_IDs = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'A1', 'A2', 'A3', '101', '102', '103', '104', '105', '106', '107', '108', 'S1']

# MENU AND SUB_MENU
MAIN_MENU = ['EXIT', 'UPDATE', 'GENERATE RENT RECEIPT', 'CHECK FOR CONSISTENCY', 'DUPLICATE RECORDS']

SUB_MENU_UPDATE = ['BACK', 'Tenant Name', 'Total Rent', 'Individual Rent', 'Tenant Count', 'Current Status']
SUB_MENU_UPDATE_TenantName = ['BACK', 'Occupancy Information', 'Payment Details']

SUB_MENU_GENERATE_RENT_RECEIPT = ['BACK', 'ROOM', 'SHOP']
SUB_MENU_GENERATE_RENT_RECEIPT_ROOM = ['BACK', 'ALL', 'SPECIFIC']
SUB_MENU_GENERATE_RENT_RECEIPT_SHOP = ['BACK', 'ALL', 'SPECIFIC']

SUB_MENU_CHECK_FOR_CONSISTENCY = ['BACK', 'Receipt Number']

SUB_MENU_DUPLICATE_RECORDS = ['BACK', 'Monthly Report Data', 'DUE Details']

# GETTING USER'S PREFERENCE
def MAIN_MENU_FUNCTION():
    print("\n\nMAIN MENU:")
    for i, Choice in enumerate(MAIN_MENU):
        print(f'{i+1})', Choice)

    while True:
        User_Choice = input('Enter Your Choice ID: ')
        if User_Choice in [str(i+1) for i in range(len(MAIN_MENU))]:
            User_Choice = int(User_Choice)
            break
        else:
            print('ID Not Defined, TRY AGAIN...')

    
    if User_Choice == 1:
        sys.exit('User TRIGGERED Exit Command')

    elif User_Choice == 2:
        def SUB_MENU_UPDATE_FUNCTION():
            print('\nSUB MENU (UPDATE):')
            for i, Choice in enumerate(SUB_MENU_UPDATE):
                print(f'{i+1})', Choice)    

            while True:
                User_Choice = input('Enter Your Choice ID: ')
                if User_Choice in [str(i+1) for i in range(len(SUB_MENU_UPDATE))]:
                    User_Choice = int(User_Choice)
                    break
                else:
                    print('ID Not Defined, TRY AGAIN...')

            if User_Choice == 1:
                MAIN_MENU_FUNCTION()

            elif User_Choice == 2:
                print('\nSUB MENU (UPDATE_TenantName):')
                for i, Choice in enumerate(SUB_MENU_UPDATE_TenantName):
                    print(f'{i+1})', Choice)    

                while True:
                    User_Choice = input('Enter Your Choice ID: ')
                    if User_Choice in [str(i+1) for i in range(len(SUB_MENU_UPDATE_TenantName))]:
                        User_Choice = int(User_Choice)
                        break
                    else:
                        print('ID Not Defined, TRY AGAIN...')

                if User_Choice == 1:
                    SUB_MENU_UPDATE_FUNCTION()

                elif User_Choice == 2:
                    Update_TenantName_Field(SUB_MENU_UPDATE_TenantName[User_Choice-1])

                elif User_Choice == 3:
                    Update_TenantName_Field(SUB_MENU_UPDATE_TenantName[User_Choice-1])
                
            elif User_Choice == 3:
                Update_TotalRent_Field()
            
            elif User_Choice == 4:
                Update_IndividualRent_Field()

            elif User_Choice == 5:
                Update_TenantsCount_Field()

            elif User_Choice == 6:
                Update_CurrentStatus_Field()

        # Calling SUB_MENU_UPDATE
        SUB_MENU_UPDATE_FUNCTION()                

    elif User_Choice == 3:
        def SUB_MENU_GENERATE_RENT_RECEIPT_FUNCTION():
            print('\nSUB MENU (GENERATE_RENT_RECEIPT):')
            for i, Choice in enumerate(SUB_MENU_GENERATE_RENT_RECEIPT):
                print(f'{i+1})', Choice)    

            while True:
                User_Choice = input('Enter Your Choice ID: ')
                if User_Choice in [str(i+1) for i in range(len(SUB_MENU_GENERATE_RENT_RECEIPT))]:
                    User_Choice = int(User_Choice)
                    break
                else:
                    print('ID Not Defined, TRY AGAIN...')

            if User_Choice == 1:
                MAIN_MENU_FUNCTION()

            elif User_Choice == 2:
                print('\nSUB MENU (GENERATE_RENT_RECEIPT_ROOM):')
                for i, Choice in enumerate(SUB_MENU_GENERATE_RENT_RECEIPT_ROOM):
                    print(f'{i+1})', Choice)    

                while True:
                    User_Choice = input('Enter Your Choice ID: ')
                    if User_Choice in [str(i+1) for i in range(len(SUB_MENU_GENERATE_RENT_RECEIPT_ROOM))]:
                        User_Choice = int(User_Choice)
                        break
                    else:
                        print('ID Not Defined, TRY AGAIN...')

                if User_Choice == 1:
                    SUB_MENU_GENERATE_RENT_RECEIPT_FUNCTION()

                elif User_Choice == 2:
                    GenerateRoomRentReceipt_ALL()

                elif User_Choice == 3:
                    GenerateRoomRentReceipt_SPECIFIC()

            elif User_Choice == 3:
                print('\nSUB MENU (GENERATE_RENT_RECEIPT_SHOP):')
                for i, Choice in enumerate(SUB_MENU_GENERATE_RENT_RECEIPT_SHOP):
                    print(f'{i+1})', Choice)    

                while True:
                    User_Choice = input('Enter Your Choice ID: ')
                    if User_Choice in [str(i+1) for i in range(len(SUB_MENU_GENERATE_RENT_RECEIPT_SHOP))]:
                        User_Choice = int(User_Choice)
                        break
                    else:
                        print('ID Not Defined, TRY AGAIN...')

                if User_Choice == 1:
                    SUB_MENU_GENERATE_RENT_RECEIPT_FUNCTION()

                elif User_Choice == 2:
                    GenerateShopRentReceipt_ALL()

                elif User_Choice == 3:
                    GenerateShopRentReceipt_SPECIFIC()

        # Calling SUB_MENU_UPDATE
        SUB_MENU_GENERATE_RENT_RECEIPT_FUNCTION()                

    elif User_Choice == 4:
        print('\nSUB MENU (CHECK_FOR_CONSISTANCY):')
        for i, Choice in enumerate(SUB_MENU_CHECK_FOR_CONSISTENCY):
            print(f'{i+1})', Choice)    

        while True:
            User_Choice = input('Enter Your Choice ID: ')
            if User_Choice in [str(i+1) for i in range(len(SUB_MENU_CHECK_FOR_CONSISTENCY))]:
                User_Choice = int(User_Choice)
                break
            else:
                print('ID Not Defined, TRY AGAIN...')

        if User_Choice == 1:
            MAIN_MENU_FUNCTION()

        elif User_Choice == 2:
            CheckConsistency_ReceiptNumber()

    elif User_Choice == 5:
        print('\nSUB MENU (DUPLICATE_RECORDS):')
        for i, Choice in enumerate(SUB_MENU_DUPLICATE_RECORDS):
            print(f'{i+1})', Choice)    

        while True:
            User_Choice = input('Enter Your Choice ID: ')
            if User_Choice in [str(i+1) for i in range(len(SUB_MENU_DUPLICATE_RECORDS))]:
                User_Choice = int(User_Choice)
                break
            else:
                print('ID Not Defined, TRY AGAIN...')

        if User_Choice == 1:
            MAIN_MENU_FUNCTION()

        elif User_Choice == 2:
            DuplicateRecords_MonthlyReportData()
        
        elif User_Choice == 3:
            DuplicateRecords_DUEDetails()
        
        print(f"Records Duplicated in the Table ({SUB_MENU_DUPLICATE_RECORDS[User_Choice-1]}) Successfully...")


# Calling MAIN_MENU
MAIN_MENU_FUNCTION()

# Close cursor and connection
cursor.close()
con.close()
