import pyodbc
import math, datetime, calendar
import os, sys
from PIL import Image, ImageDraw, ImageFont
from prettytable import PrettyTable

# OTHER FUNCTIONS
def PrintSetup_ROOM(ReceiptNumber, TenantName):
    Receipt_1 = Image.open(rf"Rent Receipts\Room {ReceiptNumber}_{TenantName}-1.jpg")
    Recepit_2 = Image.open(rf"Rent Receipts\Room {ReceiptNumber}_{TenantName}-2.jpg")

    PrintSetup = Image.new('RGB', (1248, 2244), (255, 255, 255))

    PrintSetup.paste(Receipt_1, (0, 0))
    PrintSetup.paste(Recepit_2, (0, Receipt_1.height))

    PrintSetup.save(rf"Final Print/Room {ReceiptNumber}_{TenantName}.pdf", dpi = (300, 300))


# UPDATE
def Update_TenantName_Field(TableName):
    if TableName == SUB_MENU_UPDATE_TenantName[1]:
        cursor.execute("SELECT [Tenant ID] FROM [Occupancy Information] WHERE [Tenant ID] IS NOT NULL order by [room/shop id];")
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

    TotalTenantCount = 0
    cursor.execute(f"SELECT [Room/Shop ID], [Tenant Count] FROM [Room/Shop Data]")
    Records = cursor.fetchall()
    for Record in Records:
        TotalTenantCount += Record[1] if Record[0] in Room_IDs else 0
        
    cursor.execute(f"SELECT SUM([Amount]) FROM [Water Purchase Details] WHERE [For The Month Of] = '{Month}'")
    Data = cursor.fetchone()
    TotalWaterCharge = math.ceil(Data[0]) if Data[0] != None else 0

    cursor.execute("SELECT * FROM [Room/Shop Data] ORDER BY [Room/Shop ID]")
    records = cursor.fetchall()
    for record in records:
        ID = record[0]
        if Month == calendar.month_name[Today.month].upper():
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
        if ID in Room_IDs:
            Total_Rent = math.ceil((Room_Rent + Other_Charges)/30 * Days_Occupied + math.ceil((Closing_Reading - Opening_Reading)*float(Current_Charge))) \
                + math.ceil(TotalWaterCharge / TotalTenantCount) if (Room_Rent + Other_Charges) != 0 else 0
        else:
            Total_Rent = math.ceil((Room_Rent + Other_Charges)/30 * Days_Occupied + math.ceil((Closing_Reading - Opening_Reading)*float(Current_Charge))) \
                                    if (Room_Rent + Other_Charges) != 0 else 0

        cursor.execute(f"UPDATE [Monthly Report Data] SET [Total Rent] = ? WHERE [Room/Shop ID] = ? AND \
                       [For The Month Of] = '{Month}';", (Total_Rent, ID))
        con.commit()
    print("'Total Rent' UPDATED Successfully...")

def Update_IndividualRent_Field():
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
    PreviousMonth = list(MonthNames.values())[(list(MonthNames.values()).index(Month))-1]

    cursor.execute(f"SELECT [Tenant ID], [Room/Shop ID] FROM [Payment Details] WHERE [For The Month Of] = '{Month}';")
    records = cursor.fetchall()
    for record in records:
        TenantID = record[0]        
        ID = record[1]

        cursor.execute(f"SELECT [Total Rent] FROM [Monthly Report Data] WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
        TotalRent = cursor.fetchone()[0]

        # Tenant Count
        if Month == calendar.month_name[Today.month].upper():
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

        cursor.execute(f"SELECT [DUE Amount] FROM [DUE Details] WHERE [Tenant ID] = '{TenantID}' AND [For The Month Of] = '{PreviousMonth}';")
        RawData = cursor.fetchone()
        BalanceDue = RawData[0] if RawData != None else 0

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
    print("'Current Status' UPDATED Successfully...")

def Update_ForTheMonthOf_Field_WaterPurchaseDetails():
    cursor.execute("SELECT [Purchase Date] FROM [Water Purchase Details] WHERE [For The Month Of] IS NULL")
    Records = cursor.fetchall()
    for Record in Records:
        Date = datetime.datetime.strptime(str(Record[0])[:10], r'%Y-%m-%d')
        Month = Date.strftime('%B').upper()
        cursor.execute(f"UPDATE [Water Purchase Details] SET [For The Month Of] = '{Month}' WHERE [Purchase Date] = ?", (Date,))
        cursor.commit()    


# GENERATE RENT RECEIPT
def GenerateRoomRentReceipt_ALL():
    Today = datetime.date.today()
    DatePreference = ''    
    while True:
        Month = input('\nEnter The Desired Month (eg. JAN or JANUARY): ').upper()
        if DatePreference == '':
            DatePreference = 'Without Month' if Month.upper() == 'WITHOUT MONTH' else ''
        Month = calendar.month_name[Today.month].upper() if Month == '' else Month
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
        if record[3] == None:
            continue
        else:
            ReceiptNumber = record[3]
        TenantName = record[4]
        ID = record[5]

        if ID not in Room_IDs:
            print('\n', '-' * 50, sep='')
            print(f"'{ID}' Is not a ROOM, So Receipt Generation SKIPPED...")
            print('-' * 50, '\n', sep='')
            continue

        cursor.execute(f"SELECT [Tenant Count], [Rent-1], [Rent-2], [Rent-3] FROM [Room/Shop Data] WHERE [Room/Shop ID] = '{ID}'")
        Datas = cursor.fetchone()
        # Tenant Count
        if Month == calendar.month_name[Today.month].upper():
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
        RawData = cursor.fetchone()
        BalanceDue = RawData[0] if RawData != None else 0

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
        Template = Image.open(r'Static Templates\Room Rent Receipt-1.jpg', mode='r')

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
        RoomID_Position = (925, 554) # + (73 - RoomIDText_Width)
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

        Template.save(rf'Rent Receipts\Room {ReceiptNumber}_{TenantName}-1.jpg', dpi = (300, 300))

        # Generating Rent Receipt-2
        Template = Image.open(r'Static Templates\Room Rent Receipt-2.jpg', mode='r')

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
        RoomID_Position = (786, 476) # + (60 - RoomIDText_Width)
        MonthAndTenantName_Position = (89, 530)
        ReceiptNumber_Position = (292, 299)
        Date_Position = (953 + (199 - Date_Width), 299)

        Draw.text(FinalAmount_Position, str(FinalAmount), Description_Colour, Description_Font)
        Draw.text(RoomID_Position, ID, Description_Colour, Description_Font)
        Draw.text(MonthAndTenantName_Position, f"{Month.capitalize()}, {Year} From {TenantName}.", Description_Colour, Description_Font)
        Draw.text(ReceiptNumber_Position, str(ReceiptNumber), ReceiptNumber_Colour, ReceiptNumber_Font)
        Draw.text(Date_Position, Date, Date_Colour, Date_Font)

        Template.save(rf'Rent Receipts\Room {ReceiptNumber}_{TenantName}-2.jpg', dpi = (300, 300))

        PrintSetup_ROOM(ReceiptNumber, TenantName)
        print(f"Rent Receipts generated for '{TenantName}'.")

def GenerateRoomRentReceipt_SPECIFIC():
    Today = datetime.date.today() 
    DatePreference = ''    
    while True:
        Month = input('\nEnter The Desired Month (eg. JAN or JANUARY): ').upper()
        if DatePreference == '':
            DatePreference = 'Without Date' if Month.upper() == 'WITHOUT DATE' else 'Without Month' \
                                            if Month.upper() == 'WITHOUT MONTH' else ''
        Month = calendar.month_name[Today.month].upper() if Month == '' else Month
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
            print('\n', '-' * 50, sep='')
            print(f"'{ID}' Is not a ROOM, So Receipt Generation SKIPPED...")
            print('-' * 50, '\n', sep='')
            continue

        cursor.execute(f"SELECT [Tenant Count], [Rent-1], [Rent-2], [Rent-3] FROM [Room/Shop Data] WHERE [Room/Shop ID] = '{ID}'")
        Datas = cursor.fetchone()
        # Tenant Count
        if Month == calendar.month_name[Today.month].upper():
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
        RawData = cursor.fetchone()
        BalanceDue = RawData[0] if RawData != None else 0

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
        Template = Image.open(r'Static Templates\Room Rent Receipt-1.jpg', mode='r')

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
        RoomID_Position = (925, 554) # + (73 - RoomIDText_Width)
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

        Template.save(rf'Rent Receipts\Room {ReceiptNumber}_{TenantName}-1.jpg', dpi = (300, 300))

        # Generating Rent Receipt-2
        Template = Image.open(r'Static Templates\Room Rent Receipt-2.jpg', mode='r')

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
        RoomID_Position = (786, 476) # + (60 - RoomIDText_Width)
        MonthAndTenantName_Position = (89, 530)
        ReceiptNumber_Position = (292, 299)
        Date_Position = (953 + (199 - Date_Width), 299)

        Draw.text(FinalAmount_Position, str(FinalAmount), Description_Colour, Description_Font)
        Draw.text(RoomID_Position, ID, Description_Colour, Description_Font)
        Draw.text(MonthAndTenantName_Position, f"{Month.capitalize()}, {Year} From {TenantName}.", Description_Colour, Description_Font)
        Draw.text(ReceiptNumber_Position, str(ReceiptNumber), ReceiptNumber_Colour, ReceiptNumber_Font)
        Draw.text(Date_Position, Date, Date_Colour, Date_Font)

        Template.save(rf'Rent Receipts\Room {ReceiptNumber}_{TenantName}-2.jpg', dpi = (300, 300))

        PrintSetup_ROOM(ReceiptNumber, TenantName)
        print(f"Rent Receipts generated for '{TenantName}'.")

def GenerateShopRentReceipt_ALL():
    Today = datetime.date.today()
    DatePreference = ''    
    while True:
        Month = input('\nEnter The Desired Month (eg. JAN or JANUARY): ').upper()
        if DatePreference == '':
            DatePreference = 'Without Month' if Month.upper() == 'WITHOUT MONTH' else ''
        Month = calendar.month_name[Today.month].upper() if Month == '' else Month
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
        if record[3] == None:
            continue
        else:
            ReceiptNumber = record[3]
        TenantName = record[4]
        ID = record[5]

        cursor.execute(f"SELECT [Shop Name (Optional)] FROM [Occupancy Information] WHERE [Room/Shop ID] = '{ID}' AND [Tenant ID] = '{TenantID}'")
        ShopName = cursor.fetchone()[0]

        if ID not in Shop_IDs:
            print('\n', '-' * 50, sep='')
            print(f"'{ID}' Is not a Shop, So Receipt Generation SKIPPED...")
            print('-' * 50, '\n', sep='')
            continue

        cursor.execute(f"SELECT [Rent-1] FROM [Room/Shop Data] WHERE [Room/Shop ID] = '{ID}'")
        Shop_Rent = cursor.fetchone()[0]

        cursor.execute(f"SELECT [DUE Amount] FROM [DUE Details] WHERE [Tenant ID] = '{TenantID}' AND [Room/Shop ID] = '{ID}' \
                       AND [For The Month Of] = '{Month}';")
        RawData = cursor.fetchone()
        BalanceDue = RawData[0] if RawData != None else 0

        cursor.execute(f"SELECT [Number Of Days Occupied], [Closing Sub-Meter Reading], [Opening Sub-Meter Reading], [Closing Date] \
                       FROM [Monthly report Data] WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
        Datas = cursor.fetchone()
        Days_Occupied = Datas[0]
        Shop_Rent = math.ceil((Shop_Rent * Days_Occupied)/30)
        UtilityCharges = FinalAmount - Shop_Rent - int(BalanceDue)
        ClosingReading = Datas[1]
        OpeningReading = Datas[2]
        RawClosingDate = Datas[3]
        ClosingDate = datetime.date.strftime(RawClosingDate, r'%d/%m/%Y')
        UnitsConsumed = ClosingReading - OpeningReading
        
        cursor.execute(f"SELECT DISTINCT [Closing Date] FROM [Monthly Report Data] WHERE [For The Month Of] = '{PreviousMonth}'")
        RawData = cursor.fetchone()
        RawOpeningDate = RawData[0] if RawData != None else '----------'
        OpeningDate = datetime.date.strftime(RawOpeningDate, r'%d/%m/%Y')

        if DatePreference == 'Without Month':
            Date = Date[-5:]
        else:
            Date = Date[-8:]
    
        # Generating Rent Receipt-1
        Template = Image.open(r'Static Templates\Shop Rent Receipt-1.jpg', mode='r')

        Description_Size, Description_Colour = 55, (0, 0, 0)
        Description_Font = ImageFont.truetype('CalibriFont Regular.ttf', Description_Size)
        Data_Size, Data_Colour = 50, (0, 0, 0)
        Data_Font = ImageFont.truetype('CalibriFont Regular.ttf', Data_Size)
        FinalAmount_Size, FinalAmount_Colour = 50, (0, 0, 0)
        FinalAmount_Font = ImageFont.truetype('CalibriFont Bold.ttf', FinalAmount_Size)
        ReceiptNumber_Size, ReceiptNumber_Colour = 50, (0, 0, 0)
        ReceiptNumber_Font = ImageFont.truetype('CalibriFont Bold.ttf', ReceiptNumber_Size)

        Draw = ImageDraw.Draw(Template)
        FinalAmountText_Width = Draw.textlength(str(FinalAmount), font=Description_Font)
        ShopIDText_Width = Draw.textlength(ID, font=Description_Font)
        Date_Width = Draw.textlength(Date, Data_Font)

        FinalAmount_Position1 = (380 + (135 - FinalAmountText_Width), 587)
        ShopID_Position = (837, 587) # + (104 - ShopIDText_Width)
        MonthAndTenantName_Position = (145, 658)
        ClosingReading_Position = (1482, 788)
        OpeningReading_Position = (1482, 861)
        UnitsConsumed_Position = (1482, 935)
        ShopRent_Position = (577, 788)
        UtilityCharges_Position = (577, 861)        
        FinalAmount_Position2 = (577, 935)
        ReceiptNumber_Position = (358, 349)
        Date_Position = (1909 + (239 - Date_Width), 349)

        Draw.text(FinalAmount_Position1, str(FinalAmount), Description_Colour, Description_Font)
        Draw.text(ShopID_Position, ID, Description_Colour, Description_Font)
        if ShopName != None:
            Draw.text(MonthAndTenantName_Position, f"{Month.capitalize()}, {Year} From Mr./Mrs. {TenantName} ({ShopName}).", Description_Colour, Description_Font)
        else:
            Draw.text(MonthAndTenantName_Position, f"{Month.capitalize()}, {Year} From Mr./Mrs. {TenantName}.", Description_Colour, Description_Font)
        Draw.text(ClosingReading_Position, f"{str(ClosingReading)}    ({ClosingDate})", Data_Colour, Data_Font)
        Draw.text(OpeningReading_Position, f"{str(OpeningReading)}    ({OpeningDate})", Data_Colour, Data_Font)
        Draw.text(UnitsConsumed_Position, str(UnitsConsumed), Data_Colour, Data_Font)
        Draw.text(ShopRent_Position, str(Shop_Rent), Data_Colour, Data_Font)
        Draw.text(UtilityCharges_Position, str(UtilityCharges), Data_Colour, Data_Font)
        Draw.text(FinalAmount_Position2, str(FinalAmount), FinalAmount_Colour, FinalAmount_Font)
        Draw.text(ReceiptNumber_Position, str(ReceiptNumber), ReceiptNumber_Colour, ReceiptNumber_Font)
        Draw.text(Date_Position, Date, Data_Colour, Data_Font)

        Template.save(rf'Rent Receipts\Shop {ReceiptNumber}_{TenantName}-1.jpg', dpi = (300, 300))

        # Generating Rent Receipt-2
        Template = Image.open(r'Static Templates\Shop Rent Receipt-2.jpg', mode='r')

        Description_Size, Description_Colour = 38, (0, 0, 0)
        Description_Font = ImageFont.truetype('CalibriFont Regular.ttf', Description_Size)
        ReceiptNumber_Size, ReceiptNumber_Colour = 38, (0, 0, 0)
        ReceiptNumber_Font = ImageFont.truetype('CalibriFont Bold.ttf', ReceiptNumber_Size)

        Draw = ImageDraw.Draw(Template)
        FinalAmountText_Width = Draw.textlength(str(FinalAmount), font=Description_Font)
        ShopIDText_Width = Draw.textlength(ID, font=Description_Font)
        Date_Width = Draw.textlength(Date, Description_Font)

        FinalAmount_Position = (333 + (95 - FinalAmountText_Width), 498)
        ShopID_Position = (654, 498) # + (72 - ShopIDText_Width)
        MonthAndTenantName_Position = (90, 548)
        ReceiptNumber_Position = (284, 306)
        Date_Position = (863 + (180 - Date_Width), 306)

        Draw.text(FinalAmount_Position, str(FinalAmount), Description_Colour, Description_Font)
        Draw.text(ShopID_Position, ID, Description_Colour, Description_Font)
        Draw.text(MonthAndTenantName_Position, f"{Month.capitalize()}-{Year[-2:]} From {TenantName} ({ShopName}).", Description_Colour, Description_Font)
        Draw.text(ReceiptNumber_Position, str(ReceiptNumber), ReceiptNumber_Colour, ReceiptNumber_Font)
        Draw.text(Date_Position, Date, Description_Colour, Description_Font)

        Template.save(rf'Rent Receipts\Shop {ReceiptNumber}_{TenantName}-2.jpg', dpi = (300, 300))

        print(f"Rent Receipts generated for '{TenantName}'.") 

def GenerateShopRentReceipt_SPECIFIC():
    Today = datetime.date.today() 
    DatePreference = ''    
    while True:
        Month = input('\nEnter The Desired Month (eg. JAN or JANUARY): ').upper()
        if DatePreference == '':
            DatePreference = 'Without Date' if Month.upper() == 'WITHOUT DATE' else 'Without Month' \
                                            if Month.upper() == 'WITHOUT MONTH' else ''
        Month = calendar.month_name[Today.month].upper() if Month == '' else Month
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
    PreviousMonth = list(MonthNames.values())[(list(MonthNames.values()).index(Month))-1]

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

        cursor.execute(f"SELECT [Shop Name (Optional)] FROM [Occupancy Information] WHERE [Room/Shop ID] = '{ID}' AND [Tenant ID] = '{TenantID}'")
        ShopName = cursor.fetchone()[0]

        if ID not in Shop_IDs:
            print('\n', '-' * 50, sep='')
            print(f"'{ID}' Is not a SHOP, So Receipt Generation SKIPPED...")
            print('-' * 50, '\n', sep='')
            continue

        cursor.execute(f"SELECT [Rent-1] FROM [Room/Shop Data] WHERE [Room/Shop ID] = '{ID}'")
        Shop_Rent = cursor.fetchone()[0]

        cursor.execute(f"SELECT [DUE Amount] FROM [DUE Details] WHERE [Tenant ID] = '{TenantID}' AND [Room/Shop ID] = '{ID}' \
                       AND [For The Month Of] = '{Month}';")
        RawData = cursor.fetchone()
        BalanceDue = RawData[0] if RawData != None else 0

        cursor.execute(f"SELECT [Number Of Days Occupied], [Closing Sub-Meter Reading], [Opening Sub-Meter Reading], [Closing Date] \
                       FROM [Monthly report Data] WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
        Datas = cursor.fetchone()
        Days_Occupied = Datas[0]
        Shop_Rent = math.ceil((Shop_Rent * Days_Occupied)/30)
        UtilityCharges = FinalAmount - Shop_Rent - int(BalanceDue)
        ClosingReading = Datas[1]
        OpeningReading = Datas[2]
        RawClosingDate = Datas[3]
        ClosingDate = datetime.date.strftime(RawClosingDate, r'%d/%m/%Y')
        UnitsConsumed = ClosingReading - OpeningReading        

        cursor.execute(f"SELECT DISTINCT [Closing Date] FROM [Monthly Report Data] WHERE [For The Month Of] = '{PreviousMonth}'")
        RawData = cursor.fetchone()
        RawOpeningDate = RawData[0] if RawData != None else '----------'
        OpeningDate = datetime.date.strftime(RawOpeningDate, r'%d/%m/%Y')

        if DatePreference == 'Without Date':
            Date = Date[-8:]
        elif DatePreference == 'Without Month':
            Date = Date[-5:]

        # Generating Rent Receipt-1
        Template = Image.open(r'Static Templates\Shop Rent Receipt-1.jpg', mode='r')

        Description_Size, Description_Colour = 55, (0, 0, 0)
        Description_Font = ImageFont.truetype('CalibriFont Regular.ttf', Description_Size)
        Data_Size, Data_Colour = 50, (0, 0, 0)
        Data_Font = ImageFont.truetype('CalibriFont Regular.ttf', Data_Size)
        FinalAmount_Size, FinalAmount_Colour = 50, (0, 0, 0)
        FinalAmount_Font = ImageFont.truetype('CalibriFont Bold.ttf', FinalAmount_Size)
        ReceiptNumber_Size, ReceiptNumber_Colour = 50, (0, 0, 0)
        ReceiptNumber_Font = ImageFont.truetype('CalibriFont Bold.ttf', ReceiptNumber_Size)

        Draw = ImageDraw.Draw(Template)
        FinalAmountText_Width = Draw.textlength(str(FinalAmount), font=Description_Font)
        ShopIDText_Width = Draw.textlength(ID, font=Description_Font)
        Date_Width = Draw.textlength(Date, Data_Font)

        FinalAmount_Position1 = (380 + (135 - FinalAmountText_Width), 587)
        ShopID_Position = (837, 587) # + (104 - ShopIDText_Width)
        MonthAndTenantName_Position = (145, 658)
        ClosingReading_Position = (1482, 788)
        OpeningReading_Position = (1482, 861)
        UnitsConsumed_Position = (1482, 935)
        RoomRent_Position = (577, 788)
        UtilityCharges_Position = (577, 861)        
        FinalAmount_Position2 = (577, 935)
        ReceiptNumber_Position = (358, 349)
        Date_Position = (1909 + (239 - Date_Width), 349)

        Draw.text(FinalAmount_Position1, str(FinalAmount), Description_Colour, Description_Font)
        Draw.text(ShopID_Position, ID, Description_Colour, Description_Font)
        if ShopName != None:
            Draw.text(MonthAndTenantName_Position, f"{Month.capitalize()}, {Year} From Mr./Mrs. {TenantName} ({ShopName}).", Description_Colour, Description_Font)
        else:
            Draw.text(MonthAndTenantName_Position, f"{Month.capitalize()}, {Year} From Mr./Mrs. {TenantName}.", Description_Colour, Description_Font)
        Draw.text(ClosingReading_Position, f"{str(ClosingReading)}    ({ClosingDate})", Data_Colour, Data_Font)
        Draw.text(OpeningReading_Position, f"{str(OpeningReading)}    ({OpeningDate})", Data_Colour, Data_Font)
        Draw.text(UnitsConsumed_Position, str(UnitsConsumed), Data_Colour, Data_Font)
        Draw.text(RoomRent_Position, str(Shop_Rent), Data_Colour, Data_Font)
        Draw.text(UtilityCharges_Position, str(UtilityCharges), Data_Colour, Data_Font)
        Draw.text(FinalAmount_Position2, str(FinalAmount), FinalAmount_Colour, FinalAmount_Font)
        Draw.text(ReceiptNumber_Position, str(ReceiptNumber), ReceiptNumber_Colour, ReceiptNumber_Font)
        Draw.text(Date_Position, Date, Data_Colour, Data_Font)

        Template.save(rf'Rent Receipts\Shop {ReceiptNumber}_{TenantName}-1.jpg', dpi = (300, 300))

        # Generating Rent Receipt-2
        Template = Image.open(r'Static Templates\Shop Rent Receipt-2.jpg', mode='r')

        Description_Size, Description_Colour = 38, (0, 0, 0)
        Description_Font = ImageFont.truetype('CalibriFont Regular.ttf', Description_Size)
        ReceiptNumber_Size, ReceiptNumber_Colour = 38, (0, 0, 0)
        ReceiptNumber_Font = ImageFont.truetype('CalibriFont Bold.ttf', ReceiptNumber_Size)

        Draw = ImageDraw.Draw(Template)
        FinalAmountText_Width = Draw.textlength(str(FinalAmount), font=Description_Font)
        ShopIDText_Width = Draw.textlength(ID, font=Description_Font)
        Date_Width = Draw.textlength(Date, Description_Font)

        FinalAmount_Position = (333 + (95 - FinalAmountText_Width), 498)
        ShopID_Position = (654, 498) # + (72 - ShopIDText_Width)
        MonthAndTenantName_Position = (90, 548)
        ReceiptNumber_Position = (284, 306)
        Date_Position = (863 + (180 - Date_Width), 306)

        Draw.text(FinalAmount_Position, str(FinalAmount), Description_Colour, Description_Font)
        Draw.text(ShopID_Position, ID, Description_Colour, Description_Font)
        Draw.text(MonthAndTenantName_Position, f"{Month.capitalize()}-{Year[-2:]} From {TenantName} ({ShopName}).", Description_Colour, Description_Font)
        Draw.text(ReceiptNumber_Position, str(ReceiptNumber), ReceiptNumber_Colour, ReceiptNumber_Font)
        Draw.text(Date_Position, Date, Description_Colour, Description_Font)

        Template.save(rf'Rent Receipts\Shop {ReceiptNumber}_{TenantName}-2.jpg', dpi = (300, 300))

        print(f"Rent Receipts generated for '{TenantName}'.") 


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
            print(f"\nRoom/Shop ID: {ID} is INCONSISTANT...")


# DUPLICATE RECORDS
def DuplicateRecords_MonthlyReportData():
    Today = datetime.date.today()
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

    Month = calendar.month_name[Today.month].upper()
    PreviousMonth = list(MonthNames.values())[(list(MonthNames.values()).index(Month))-1]
    
    cursor.execute(f"SELECT [Room/Shop ID], [Closing Sub-Meter Reading] FROM [Monthly Report Data] WHERE [For The Month Of] = '{PreviousMonth}';")
    Records = cursor.fetchall()
    for Record in Records:
        ID = Record[0]
        OpeningReading = Record[1]
        cursor.execute(f"INSERT INTO [Monthly Report Data] ([Room/Shop ID], [Opening Sub-Meter Reading], [Closing Date], [For The Month Of]) \
                       VALUES (?, ?, ?, ?);", (ID, OpeningReading, Date, Month))
        cursor.commit()     

def DuplicateRecords_DUEDetails():
    Today = datetime.date.today()
    Month = calendar.month_name[Today.month].upper()
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

def DuplicateRecords_PaymentDetails():
    Today = datetime.date.today()
    Month = calendar.month_name[Today.month].upper()
    Year = Today.strftime(r'%Y')

    cursor.execute("SELECT MAX([Receipt Number]) FROM [Payment Details]")
    ReceiptNumber = int(cursor.fetchone()[0]) + 1

    for ID in list(Room_IDs + Shop_IDs):
        cursor.execute(f"SELECT [Tenant ID], [Tenant Name] FROM [Occupancy Information] \
                       WHERE [Room/Shop ID] = '{ID}' AND [To (Date)] IS NULL AND [Tenant ID] IS NOT NULL ORDER BY [Room/Shop ID]")
        Records = cursor.fetchall()
        if Records != []:
            for Record in Records:
                cursor.execute(f"INSERT INTO [Payment Details] \
                               ([Receipt Number], [Tenant ID], [Tenant Name], [Room/Shop ID], [For The Month Of], [Year (YYYY)]) \
                               VALUES ({ReceiptNumber}, '{Record[0]}', '{Record[1]}', '{ID}', '{Month}', '{Year}');")
                cursor.commit()     
                ReceiptNumber += 1


# FETCH DATA
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

def FetchData_UNPAID_Tenants():
    cursor.execute("SELECT [Tenant ID], [Tenant Name], [Room/Shop ID], [Individual Rent], [For The Month OF] \
                   FROM [Payment Details] WHERE Status = 'UNPAID' ORDER BY [Room/Shop ID]")
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

    print()
    print(DetailsTable)

    SUMTable = PrettyTable()
    SUMTable.field_names = ['Total DUE', 'For The Month Of']
    cursor.execute("SELECT SUM([Individual Rent]), [For The Month Of] \
                   FROM [Payment Details] WHERE Status = 'UNPAID' GROUP BY [For The Month Of] ORDER BY SUM([Individual Rent])")
    RawRecords = cursor.fetchall()

    for Record in RawRecords:
        Record = list(Record)
        Record[0] = '{:,}'.format(int(Record[0]))
        SUMTable.add_row(Record)

    print()
    print(SUMTable)

def FetchData_OccupiedSpaceID_FROM_TenantID():
    print("\n\n----ENTER 'STOP' TO QUIT----")
    while True:
        TenantID = input('\nEnter The Tenant ID To Fetch Room/Shop ID: ').strip()
        if TenantID.upper() == 'STOP':
            break
        
        if TenantID.isdigit():
            TenantID = "{:04d}".format(int(TenantID))
        else:
            print('INVALID Tenant ID, TRY AGAIN...')
            continue
            
        cursor.execute(f"SELECT [Room/Shop ID] FROM [Occupancy Information] WHERE [Tenant ID] = '{TenantID}' AND [To (Date)] IS NULL;")
        Records = cursor.fetchall()

        if Records != []:
            print(f"\nTenant With ID '{TenantID}' Currently Occupying Room/Shop_ID(s): ", end='')
            for Record in Records:
                print(f'{Record[0]}', end=', ') if Record != Records[-1] else print(Record[0])
        else:
            print('No Records Found, TRY AGAIN...')

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
    
def FetchData_TotalCashReceived():
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

    cursor.execute(f"SELECT SUM([Total Rent]) FROM [Monthly Report Data] WHERE [For The Month Of] = '{Month}'")
    TotalCashReceived = int(cursor.fetchone()[0])
    TotalCashReceived = '{:,}'.format(TotalCashReceived)
    print(f'\nTotal Cash Received For The Month Of {Month}:', TotalCashReceived)

def FetchData_UnitsConsumed():
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

    cursor.execute(f"SELECT [Room/Shop ID], [Closing Sub-Meter Reading], [Opening Sub-Meter Reading] FROM [Monthly Report Data] \
                   WHERE [For The Month Of] = '{Month}' ORDER BY [Room/Shop ID];")
    Records = cursor.fetchall()

    Table = PrettyTable()
    Table.field_names = ['Room/Shop ID', 'Units Consumed']
    for Record in Records:
        UnitsConsumed = round(Record[1] - Record[2], 1) if Record[1] != None and Record[2] != None else '----'
        print((Record[0], UnitsConsumed))
        Table.add_row([Record[0], UnitsConsumed])

    print()
    print(Table)

# Establish Connection
try:
    con = pyodbc.connect(r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=D:\Python Projects\Smart-Mansion-Management\Database (MS Access).accdb;')
except:
    print('Database Connection FAILED') 

# Create a Cursor
cursor = con.cursor()

# Global Variables
MonthNames = {'JAN': 'JANUARY', 'FEB': 'FEBRUARY', 'MAR': 'MARCH', 'APR': 'APRIL', 'MAY': 'MAY', 'JUN': 'JUNE', 'JUL': 'JULY', 'AUG': 'AUGUST', 'SEP': 'SEPTEMBER', 'OCT': 'OCTOBER', 'NOV': 'NOVEMBER', 'DEC': 'DECEMBER'}
Room_IDs = ['202', '203', '204', '205', '206', '207', '208', '301', '302', '303', '304', '305', '306', '307', '308', 'S2', 'S3']
Shop_IDs = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'A1', 'A2', 'A3', '101', '102', '103', '104', '105', '106', '107', '108', 'S1', 'MILL']

# MENU AND SUB_MENU
MAIN_MENU = ['EXIT', 'UPDATE', 'GENERATE RENT RECEIPT', 'CHECK FOR CONSISTENCY', 'DUPLICATE RECORDS', 'FETCH DATA', 'CUSTOM ACTION']

SUB_MENU_UPDATE = ['BACK', 'Tenant Name', 'Total Rent', 'Individual Rent', 'Tenant Count', 'Current Status', 'For The Month Of']
SUB_MENU_UPDATE_TenantName = ['BACK', 'Occupancy Information', 'Payment Details']

SUB_MENU_GENERATE_RENT_RECEIPT = ['BACK', 'ROOM', 'SHOP']
SUB_MENU_GENERATE_RENT_RECEIPT_ROOM = ['BACK', 'ALL', 'SPECIFIC']
SUB_MENU_GENERATE_RENT_RECEIPT_SHOP = ['BACK', 'ALL', 'SPECIFIC']

SUB_MENU_CHECK_FOR_CONSISTENCY = ['BACK', 'Receipt Number', 'Room_ID AND Shop_ID']

SUB_MENU_DUPLICATE_RECORDS = ['BACK', 'Monthly Report Data', 'DUE Details', 'Payment Details']

SUB_MENU_FETCH_DATA = ['BACK', 'Tenant_ID --> Tenant_Name', 'Tenant_Name --> Tenant_ID', 'Room/Shop_ID --> TenantID', \
                       'UNPAID Tenants', 'Get Tenant Details', 'Vacant Room/Shop', 'Total Cash Received', 'Units Consumed']

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

                    input('\nPress ENTER Key To Continue...')
                    MAIN_MENU_FUNCTION()

                elif User_Choice == 3:
                    Update_TenantName_Field(SUB_MENU_UPDATE_TenantName[User_Choice-1])

                    input('\nPress ENTER Key To Continue...')
                    MAIN_MENU_FUNCTION()
                
            elif User_Choice == 3:
                Update_TotalRent_Field()

                input('\nPress ENTER Key To Continue...')
                MAIN_MENU_FUNCTION()
            
            elif User_Choice == 4:
                Update_IndividualRent_Field()

                input('\nPress ENTER Key To Continue...')
                MAIN_MENU_FUNCTION()

            elif User_Choice == 5:
                Update_TenantsCount_Field()

                input('\nPress ENTER Key To Continue...')
                MAIN_MENU_FUNCTION()

            elif User_Choice == 6:
                Update_CurrentStatus_Field()

                input('\nPress ENTER Key To Continue...')
                MAIN_MENU_FUNCTION()

            elif User_Choice == 7:
                Update_ForTheMonthOf_Field_WaterPurchaseDetails()

                print(f"'{SUB_MENU_UPDATE[User_Choice-1]}' Field UPDATED Successfully...")
                input('\nPress ENTER Key To Continue...')
                MAIN_MENU_FUNCTION()

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

                    input('\nPress ENTER Key To Continue...')
                    MAIN_MENU_FUNCTION()

                elif User_Choice == 3:
                    GenerateRoomRentReceipt_SPECIFIC()

                    input('\nPress ENTER Key To Continue...')
                    MAIN_MENU_FUNCTION()

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

                    input('\nPress ENTER Key To Continue...')
                    MAIN_MENU_FUNCTION()

                elif User_Choice == 3:
                    GenerateShopRentReceipt_SPECIFIC()

                    input('\nPress ENTER Key To Continue...')
                    MAIN_MENU_FUNCTION()

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

            input('\nPress ENTER Key To Continue...')
            MAIN_MENU_FUNCTION()

        elif User_Choice == 3:
            CheckConsistency_ID()

            input('\nPress ENTER Key To Continue...')
            MAIN_MENU_FUNCTION()

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

            print(f"Records Duplicated in the Table ({SUB_MENU_DUPLICATE_RECORDS[User_Choice-1]}) Successfully...")
            input('\nPress ENTER Key To Continue...')
            MAIN_MENU_FUNCTION()
        
        elif User_Choice == 3:
            DuplicateRecords_DUEDetails()

            print(f"Records Duplicated in the Table ({SUB_MENU_DUPLICATE_RECORDS[User_Choice-1]}) Successfully...")
            input('\nPress ENTER Key To Continue...')
            MAIN_MENU_FUNCTION()

        elif User_Choice == 4:
            DuplicateRecords_PaymentDetails()

            print(f"Records Duplicated in the Table ({SUB_MENU_DUPLICATE_RECORDS[User_Choice-1]}) Successfully...")
            input('\nPress ENTER Key To Continue...')
            MAIN_MENU_FUNCTION()
        
    elif User_Choice == 6:
        print('\nSUB MENU (FETCH_DATA):')
        for i, Choice in enumerate(SUB_MENU_FETCH_DATA):
            print(f'{i+1})', Choice)    

        while True:
            User_Choice = input('Enter Your Choice ID: ')
            if User_Choice in [str(i+1) for i in range(len(SUB_MENU_FETCH_DATA))]:
                User_Choice = int(User_Choice)
                break
            else:
                print('ID Not Defined, TRY AGAIN...')

        if User_Choice == 1:
            MAIN_MENU_FUNCTION()

        elif User_Choice == 2:
            FetchData_TenantName_FROM_TenantID()

            input('\nPress ENTER Key To Continue...')
            MAIN_MENU_FUNCTION()

        elif User_Choice == 3:
            FetchData_TenantID_FROM_TenantName()

            input('\nPress ENTER Key To Continue...')
            MAIN_MENU_FUNCTION()

        elif User_Choice == 4:
            FetchData_OccupiedSpaceID_FROM_TenantID()

            input('\nPress ENTER Key To Continue...')
            MAIN_MENU_FUNCTION()

        elif User_Choice == 5:
            FetchData_UNPAID_Tenants()

            input('\nPress ENTER Key To Continue...')
            MAIN_MENU_FUNCTION()

        elif User_Choice == 6:
            FetchData_GetTenantDetails()

            input('\nPress ENTER Key To Continue...')
            MAIN_MENU_FUNCTION()

        elif User_Choice == 7:
            FetchDate_Vacancy()

            input('\nPress ENTER Key To Continue...')
            MAIN_MENU_FUNCTION()

        elif User_Choice == 8:
            FetchData_TotalCashReceived()

            input('\nPress ENTER Key To Continue...')
            MAIN_MENU_FUNCTION()

        elif User_Choice == 9:
            FetchData_UnitsConsumed()

            input('\nPress ENTER Key To Continue...')
            MAIN_MENU_FUNCTION()

# Calling MAIN_MENU
MAIN_MENU_FUNCTION()


# Close cursor and connection
cursor.close()
con.close()
