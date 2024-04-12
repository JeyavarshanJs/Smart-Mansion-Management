import datetime, calendar, math
import os, shutil
import win32file
from PIL import Image, ImageDraw, ImageFont

from CustomModules.VariablesModule import *
from CustomModules.EstablishConnection import *

# GENERATE RENT RECEIPT
def GenerateRoomRentReceipt_ALL():
    Today = datetime.date.today()
    DatePreference = ''    
    while True:
        Month = input('\nEnter The Desired Month (eg. JAN or JANUARY): ').strip().upper()
        if DatePreference == '':
            DatePreference = 'Without Month' if Month.upper() == 'WITHOUT MONTH' else ''
            if DatePreference != '':
                print('Preference ACCEPTED...')
        Month = calendar.month_name[Today.month-1].upper() if Month == '' else Month
        if Month in MonthNames.keys():
            Month = MonthNames[Month]
            break
        elif Month in MonthNames.values():
            break
        else:            
            print('INVALID Month Name, TRY AGAIN...')
    PreviousMonth = list(MonthNames.values())[(list(MonthNames.values()).index(Month))-1]

    print('\n<<<<<<<<<<+>>>>>>>>>>')
    Date = Today.strftime(r'%d/%m/%Y')
    cursor.execute(f"SELECT [Tenant ID], [Individual Rent], [Year (YYYY)], [Receipt Number], [Tenant Name], [Room/Shop ID] \
                   FROM [Payment Details] WHERE [Status] = 'UNPAID' AND [For The Month Of] = '{Month}';")
    Records = cursor.fetchall()
    for Record in Records:
        TenantID = Record[0]
        FinalAmount= int(Record[1])
        Year = Record[2]
        if Record[3] == None:
            continue
        else:
            ReceiptNumber = Record[3]
        TenantName = Record[4]
        ID = Record[5]

        if ID not in Room_IDs:
            print('\n', '-' * 50, sep='')
            print(f"'{ID}' Is not a ROOM, So Receipt Generation SKIPPED...")
            print('-' * 50, '\n', sep='')
            continue

        cursor.execute(f"SELECT [Tenant Count], [Rent-1], [Rent-2], [Rent-3] FROM [Room/Shop Data] WHERE [Room/Shop ID] = '{ID}'")
        Data = cursor.fetchone()
        # Tenant Count
        if Month == calendar.month_name[Today.month-1].upper():
            TenantCount = Data[0]
        else:
            while True:
                TenantCount = input(f'\nEnter Tenant Count For The Room/Shop (ID: {ID}): ')
                if TenantCount in ['1', '2', '3']:
                    TenantCount = int(TenantCount)
                    break
                else:
                    print('INVALID Tenant Count, TRY AGAIN...')
        Room_Rent = math.ceil((Data[TenantCount])/TenantCount) if TenantCount != 0 else 0

        cursor.execute(f"SELECT [DUE Amount] FROM [DUE Details] WHERE [Tenant ID] = '{TenantID}' AND [Room/Shop ID] = '{ID}' \
                       AND [For The Month Of] = '{PreviousMonth}';")
        RawData = cursor.fetchone()
        BalanceDue = int(RawData[0]) if RawData != None else 0

        cursor.execute(f"SELECT [Number Of Days Occupied], [Closing Sub-Meter Reading], [Opening Sub-Meter Reading] \
                       FROM [Monthly report Data] WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
        Data = cursor.fetchone()
        Days_Occupied = Data[0]
        Room_Rent = math.ceil((Room_Rent * Days_Occupied)/30)
        UtilityCharges = FinalAmount - Room_Rent - BalanceDue
        ClosingReading = round(Data[1], 1)
        OpeningReading = round(Data[2], 1)
        UnitsConsumed = round(ClosingReading - OpeningReading, 1)
        
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
        RoomID_Position = (925 + (73 - RoomIDText_Width)/2, 554)
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
        RoomID_Position = (786 + (60 - RoomIDText_Width)/2, 476)
        MonthAndTenantName_Position = (89, 530)
        ReceiptNumber_Position = (292, 299)
        Date_Position = (953 + (199 - Date_Width), 299)

        Draw.text(FinalAmount_Position, str(FinalAmount), Description_Colour, Description_Font)
        Draw.text(RoomID_Position, ID, Description_Colour, Description_Font)
        Draw.text(MonthAndTenantName_Position, f"{Month.capitalize()}, {Year} From {TenantName}.", Description_Colour, Description_Font)
        Draw.text(ReceiptNumber_Position, str(ReceiptNumber), ReceiptNumber_Colour, ReceiptNumber_Font)
        Draw.text(Date_Position, Date, Date_Colour, Date_Font)

        Template.save(rf'Rent Receipts\Room {ReceiptNumber}_{TenantName}-2.jpg', dpi = (300, 300))

        print(f"\nRent Receipts generated for '{TenantName}'.")
        PrintSetup_ROOM(ReceiptNumber, TenantName)
    print('\n<<<<<<<<<<+>>>>>>>>>>\n')

def GenerateRoomRentReceipt_SPECIFIC(Month = None, ReceiptNumber_List = None):
    Today = datetime.date.today() 
    DatePreference = ''
    if Month == None:    
        while True:
            Month = input('\nEnter The Desired Month (eg. JAN or JANUARY): ').strip().upper()
            if DatePreference == '':
                DatePreference = 'Without Date' if Month.upper() == 'WITHOUT DATE' else 'Without Month' \
                                                if Month.upper() == 'WITHOUT MONTH' else ''
                if DatePreference != '':
                    print('Preference ACCEPTED...')
            Month = calendar.month_name[Today.month-1].upper() if Month == '' else Month
            if Month in MonthNames.keys():
                Month = MonthNames[Month]
                break
            elif Month in MonthNames.values():
                break
            else:            
                print('INVALID Month Name, TRY AGAIN...')
    else:
        while True:
            RawData = input('Enter Your Preference (OPTIONAL): ').strip().upper()
            if DatePreference == '' and RawData != '':
                DatePreference = 'Without Date' if RawData.upper() == 'WITHOUT DATE' else 'Without Month' \
                                                if RawData.upper() == 'WITHOUT MONTH' else ''
                if DatePreference != '':
                    print('Preference ACCEPTED...')
                    break
                else:
                    print('INVALID Entry, TRY AGAIN...')
            else:
                break
    PreviousMonth = list(MonthNames.values())[(list(MonthNames.values()).index(Month))-1]

    if ReceiptNumber_List == None:
        IsRunning = True
        while IsRunning:
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
                        IsRunning = False
                    else:
                        print('INVALID Receipt Numbers, TRY AGAIN...')
                        IsRunning = True
                        break
                    ReceiptNumber_List.extend([_ for _ in range(StartID, EndID+1)])
                else:
                    if i.isdigit():
                        ReceiptNumber_List.append(int(i))
                        IsRunning = False
                    else:
                        print('INVALID Receipt Numbers, TRY AGAIN...')
                        IsRunning = True
                        break

            if not IsRunning:
                x = 0
                for i in ReceiptNumber_List:
                    cursor.execute(f"SELECT [Tenant Name], [Room/Shop ID] FROM [Payment Details] WHERE [Receipt Number] = {i} AND [Status] = 'UNPAID' \
                                    AND [For The Month OF] = '{Month}';")
                    RawDataS = cursor.fetchone()
                    cursor.execute(f"SELECT [Tenant Name], [Room/Shop ID] FROM [Payment Details (NS)] WHERE [Receipt Number] = {i} AND [Status] = 'UNPAID' \
                                    AND [For The Month OF] = '{Month}';")
                    RawDataNS = cursor.fetchone()

                    x += 1 if RawDataS != None or RawDataNS != None else 0

                if len(ReceiptNumber_List) != x:
                    print('Some Tenant ID Are NOT VALID, Try Again...')      
                    IsRunning = True      
                else:
                    break

    print('\n<<<<<<<<<<+>>>>>>>>>>')
    Date = Today.strftime(r'%d/%m/%Y')
    for ReceiptNumber in ReceiptNumber_List:
        # FETCHING DATA
        cursor.execute(f"SELECT [Individual Rent], [Year (YYYY)], [Tenant ID], [Tenant Name], [Room/Shop ID] FROM [Payment Details] \
                       WHERE [Receipt Number] = {ReceiptNumber};")
        RawDataS = cursor.fetchone()
        cursor.execute(f"SELECT [Individual Rent], [Year (YYYY)], [Tenant ID], [Tenant Name], [Room/Shop ID] FROM [Payment Details (NS)] \
                       WHERE [Receipt Number] = {ReceiptNumber};")
        RawDataNS = cursor.fetchone()
        
        Record = RawDataS if RawDataS != None else RawDataNS
        FinalAmount= int(Record[0])
        Year = Record[1]
        TenantID = Record[2]
        TenantName = Record[3]
        ID = Record[4]

        if ID not in Room_IDs:
            print('\n', '-' * 50, sep='')
            print(f"'{ID}' Is not a ROOM, So Receipt Generation SKIPPED...")
            print('-' * 50, '\n', sep='')
            continue

        cursor.execute(f"SELECT [Tenant Count], [Rent-1], [Rent-2], [Rent-3] FROM [Room/Shop Data] WHERE [Room/Shop ID] = '{ID}'")
        Data = cursor.fetchone()
        # Tenant Count
        if Month == calendar.month_name[Today.month-1].upper() or Month == calendar.month_name[Today.month].upper():
            TenantCount = Data[0]
        else:
            while True:
                TenantCount = input(f'\nEnter Tenant Count For The Room/Shop (ID: {ID}): ')
                if TenantCount in ['1', '2', '3']:
                    TenantCount = int(TenantCount)
                    break
                else:
                    print('INVALID Tenant Count, TRY AGAIN...')
        Room_Rent = math.ceil((Data[TenantCount])/TenantCount) if TenantCount != 0 else 0

        cursor.execute(f"SELECT [DUE Amount] FROM [DUE Details] WHERE [Tenant ID] = '{TenantID}' AND [Room/Shop ID] = '{ID}' \
                       AND [For The Month Of] = '{PreviousMonth}';")
        RawData = cursor.fetchone()
        BalanceDue = int(RawData[0]) if RawData != None else 0

        if Month == calendar.month_name[Today.month].upper():
            cursor.execute(f"SELECT [Number Of Days Occupied], [Closing Sub-Meter Reading], [Opening Sub-Meter Reading] FROM [Unusual Departure Details] \
                WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
            Data = cursor.fetchone()
        else:
            cursor.execute(f"SELECT [Number Of Days Occupied], [Closing Sub-Meter Reading], [Opening Sub-Meter Reading] FROM [Monthly report Data] \
                WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
            Data = cursor.fetchone()

        Days_Occupied = Data[0]
        Room_Rent = math.ceil((Room_Rent * Days_Occupied)/30)
        UtilityCharges = FinalAmount - Room_Rent - BalanceDue
        ClosingReading = round(Data[1], 1)
        OpeningReading = round(Data[2], 1)
        UnitsConsumed = round(ClosingReading - OpeningReading, 1)

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
        RoomID_Position = (925 + (73 - RoomIDText_Width)/2, 554)
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
        RoomID_Position = (786 + (60 - RoomIDText_Width)/2, 476)
        MonthAndTenantName_Position = (89, 530)
        ReceiptNumber_Position = (292, 299)
        Date_Position = (953 + (199 - Date_Width), 299)

        Draw.text(FinalAmount_Position, str(FinalAmount), Description_Colour, Description_Font)
        Draw.text(RoomID_Position, ID, Description_Colour, Description_Font)
        Draw.text(MonthAndTenantName_Position, f"{Month.capitalize()}, {Year} From {TenantName}.", Description_Colour, Description_Font)
        Draw.text(ReceiptNumber_Position, str(ReceiptNumber), ReceiptNumber_Colour, ReceiptNumber_Font)
        Draw.text(Date_Position, Date, Date_Colour, Date_Font)

        Template.save(rf'Rent Receipts\Room {ReceiptNumber}_{TenantName}-2.jpg', dpi = (300, 300))

        print(f"\nRent Receipts generated for '{TenantName}'.")
        PrintSetup_ROOM(ReceiptNumber, TenantName)
    print('\n<<<<<<<<<<+>>>>>>>>>>\n')

    # print('\n<<<<<<<<<<+>>>>>>>>>>')
    # if ChoosePrinter == None:
    #     IsPrinterAvailable = False
    #     ActivePrinters, IsPrinterAvailable = GETPrinters()
    #     if IsPrinterAvailable:
    #         UserPreference = input('Do You Want To Print The Receipts? (Y/N): ').strip().upper()
    #         if UserPreference == 'Y' or UserPreference == '':
    #                 ChoosePrinter(ActivePrinters)
    #                 Print(ReceiptNumber_List, 1057, 1900, 'ROOM')
    # else:
    #     Print(ReceiptNumber_List, 1057, 1900, 'ROOM')

    #     Print(rf"Final Print/Room {ReceiptNumber}_{TenantName}.pdf", )

def GenerateShopRentReceipt_ALL():
    Today = datetime.date.today()
    DatePreference = ''    
    while True:
        Month = input('\nEnter The Desired Month (eg. JAN or JANUARY): ').strip().upper()
        if DatePreference == '':
            DatePreference = 'Without Month' if Month.upper() == 'WITHOUT MONTH' else ''
            if DatePreference != '':
                print('Preference ACCEPTED...')
        if Month in MonthNames.keys():
            Month = MonthNames[Month]
            break
        elif Month in MonthNames.values():
            break
        else:            
            print('INVALID Month Name, TRY AGAIN...')
    PreviousMonth = list(MonthNames.values())[(list(MonthNames.values()).index(Month))-1]

    print('\n<<<<<<<<<<+>>>>>>>>>>')
    Date = Today.strftime(r'%d/%m/%Y')
    cursor.execute(f"SELECT [Tenant ID], [Individual Rent], [Year (YYYY)], [Receipt Number], [Tenant Name], [Room/Shop ID] \
                   FROM [Payment Details] WHERE [Status] = 'UNPAID' AND [For The Month Of] = '{Month}';")
    Records = cursor.fetchall()
    for Record in Records:
        TenantID = Record[0]
        FinalAmount= int(Record[1])
        Year = Record[2]
        if Record[3] == None:
            continue
        else:
            ReceiptNumber = Record[3]
        TenantName = Record[4]
        ID = Record[5]

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
                       AND [For The Month Of] = '{PreviousMonth}';")
        RawData = cursor.fetchone()
        BalanceDue = int(RawData[0]) if RawData != None else 0

        cursor.execute(f"SELECT [Number Of Days Occupied], [Closing Sub-Meter Reading], [Opening Sub-Meter Reading], [Closing Date] \
                       FROM [Monthly report Data] WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
        Data = cursor.fetchone()
        Days_Occupied = Data[0]
        Shop_Rent = math.ceil((Shop_Rent * Days_Occupied)/30)
        UtilityCharges = FinalAmount - Shop_Rent - BalanceDue if ID != 'MILL' else FinalAmount - Shop_Rent
        ClosingReading = round(Data[1], 1)
        OpeningReading = round(Data[2], 1)
        RawClosingDate = Data[3]
        ClosingDate = datetime.date.strftime(RawClosingDate, r'%d/%m/%Y')
        UnitsConsumed = round(ClosingReading - OpeningReading, 1)
        
        cursor.execute(f"SELECT DISTINCT [Closing Date] FROM [Monthly Report Data] WHERE [For The Month Of] = '{PreviousMonth}'")
        RawData = cursor.fetchone()
        RawOpeningDate = RawData[0] if RawData != None else '----------'
        OpeningDate = datetime.date.strftime(RawOpeningDate, r'%d/%m/%Y') if RawOpeningDate != '----------' else '----------'

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

        FinalAmount_Position1 = (380 + (135 - FinalAmountText_Width), 577)
        ShopID_Position = (832 + (104 - ShopIDText_Width)/2, 577)
        MonthAndTenantName_Position = (145, 648)
        ClosingReading_Position = (1482, 778)
        OpeningReading_Position = (1482, 851)
        UnitsConsumed_Position = (1482, 925)
        ShopRent_Position = (577, 778)
        UtilityCharges_Position = (577, 851)        
        FinalAmount_Position2 = (577, 925)
        ReceiptNumber_Position = (358, 339)
        Date_Position = (1909 + (239 - Date_Width), 339)

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

        Description_Size, Description_Colour = 42, (0, 0, 0)
        Description_Font = ImageFont.truetype('CalibriFont Regular.ttf', Description_Size)
        Date_Size, Date_Colour = 38, (0, 0, 0)
        Date_Font = ImageFont.truetype('CalibriFont Regular.ttf', Date_Size)
        ReceiptNumber_Size, ReceiptNumber_Colour = 38, (0, 0, 0)
        ReceiptNumber_Font = ImageFont.truetype('CalibriFont Bold.ttf', ReceiptNumber_Size)

        Draw = ImageDraw.Draw(Template)
        FinalAmountText_Width = Draw.textlength(str(FinalAmount), font=Description_Font)
        ShopIDText_Width = Draw.textlength(ID, font=Description_Font)
        Date_Width = Draw.textlength(Date, Description_Font)

        FinalAmount_Position = (372 + (104 - FinalAmountText_Width), 512)
        ShopID_Position = (758 + (80 - ShopIDText_Width)/2, 512)
        MonthAndTenantName_Position = (258, 567)
        ReceiptNumber_Position = (284, 307)
        Date_Position = (864 + (180 - Date_Width), 307)

        Draw.text(FinalAmount_Position, str(FinalAmount), Description_Colour, Description_Font)
        Draw.text(ShopID_Position, ID, Description_Colour, Description_Font)
        Draw.text(MonthAndTenantName_Position, f"{Month.capitalize()}-{Year[-2:]} From {TenantName}.", Description_Colour, Description_Font)
        Draw.text(ReceiptNumber_Position, str(ReceiptNumber), ReceiptNumber_Colour, ReceiptNumber_Font)
        Draw.text(Date_Position, Date, Date_Colour, Date_Font)

        Template.save(rf'Rent Receipts\Shop {ReceiptNumber}_{TenantName}-2.jpg', dpi = (300, 300))

        print(f"\nRent Receipts generated for '{TenantName}'.") 
        PrintSetup_SHOP_1(ReceiptNumber, TenantName)
        PrintSetup_SHOP_2(ReceiptNumber, TenantName)
    print('\n<<<<<<<<<<+>>>>>>>>>>\n')

def GenerateShopRentReceipt_SPECIFIC(Month = None, ReceiptNumber_List = None):
    Today = datetime.date.today() 
    DatePreference = ''    
    if Month == None:    
        while True:
            Month = input('\nEnter The Desired Month (eg. JAN or JANUARY): ').strip().upper()
            if DatePreference == '':
                DatePreference = 'Without Date' if Month.upper() == 'WITHOUT DATE' else 'Without Month' \
                                                if Month.upper() == 'WITHOUT MONTH' else ''
                if DatePreference != '':
                    print('Preference ACCEPTED...')
            Month = calendar.month_name[Today.month-1].upper() if Month == '' else Month
            if Month in MonthNames.keys():
                Month = MonthNames[Month]
                break
            elif Month in MonthNames.values():
                break
            else:            
                print('INVALID Month Name, TRY AGAIN...')
    else:
        while True:
            RawData = input('Enter Your Preference (OPTIONAL): ').strip().upper()
            if DatePreference == '' and RawData != '':
                DatePreference = 'Without Date' if RawData.upper() == 'WITHOUT DATE' else 'Without Month' \
                                                if RawData.upper() == 'WITHOUT MONTH' else ''
                if DatePreference != '':
                    print('Preference ACCEPTED...')
                    break
                else:
                    print('INVALID Entry, TRY AGAIN...')
            else:
                break
    PreviousMonth = list(MonthNames.values())[(list(MonthNames.values()).index(Month))-1]

    if ReceiptNumber_List == None:
        IsRunning = True
        while IsRunning:
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
                        IsRunning = False
                    else:
                        print('INVALID Receipt Numbers, TRY AGAIN...')
                        IsRunning = True
                        break
                    ReceiptNumber_List.extend([_ for _ in range(StartID, EndID+1)])
                else:
                    if i.isdigit():
                        ReceiptNumber_List.append(int(i))
                        IsRunning = False
                    else:
                        print('INVALID Receipt Numbers, TRY AGAIN...')
                        IsRunning = True
                        break
            x = 0
            for i in ReceiptNumber_List:
                    cursor.execute(f"SELECT [Tenant Name], [Room/Shop ID] FROM [Payment Details] WHERE [Receipt Number] = {i} AND [Status] = 'UNPAID' \
                                    AND [For The Month OF] = '{Month}';")
                    RawDataS = cursor.fetchone()
                    cursor.execute(f"SELECT [Tenant Name], [Room/Shop ID] FROM [Payment Details (NS)] WHERE [Receipt Number] = {i} AND [Status] = 'UNPAID' \
                                    AND [For The Month OF] = '{Month}';")
                    RawDataNS = cursor.fetchone()

                    x += 1 if RawDataS != None or RawDataNS != None else 0

            if len(ReceiptNumber_List) != x:
                print('Some Tenant ID Are NOT VALID, Try Again...') 
                IsRunning = True           
            else:
                break

    print('\n<<<<<<<<<<+>>>>>>>>>>')
    Date = Today.strftime(r'%d/%m/%Y')
    for ReceiptNumber in ReceiptNumber_List:
        # FETCHING DATA
        cursor.execute(f"SELECT [Individual Rent], [Year (YYYY)], [Tenant ID], [Tenant Name], [Room/Shop ID] FROM [Payment Details] \
                       WHERE [Receipt Number] = {ReceiptNumber};")
        RawDataS = cursor.fetchone()
        cursor.execute(f"SELECT [Individual Rent], [Year (YYYY)], [Tenant ID], [Tenant Name], [Room/Shop ID] FROM [Payment Details (NS)] \
                       WHERE [Receipt Number] = {ReceiptNumber};")
        RawDataNS = cursor.fetchone()
        
        Record = RawDataS if RawDataS != None else RawDataNS
        FinalAmount= int(Record[0])
        Year = Record[1]
        TenantID = Record[2]
        TenantName = Record[3]
        ID = Record[4]

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
                       AND [For The Month Of] = '{PreviousMonth}';")
        RawData = cursor.fetchone()
        BalanceDue = int(RawData[0]) if RawData != None else 0

        if Month == calendar.month_name[Today.month].upper():
            cursor.execute(f"SELECT [Number Of Days Occupied], [Closing Sub-Meter Reading], [Opening Sub-Meter Reading], [Closing Date] \
                FROM [Unusual Departure Details] WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
            Data = cursor.fetchone()
        else:
            cursor.execute(f"SELECT [Number Of Days Occupied], [Closing Sub-Meter Reading], [Opening Sub-Meter Reading], [Closing Date] \
                FROM [Monthly report Data] WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
            Data = cursor.fetchone()

        Days_Occupied = Data[0]
        Shop_Rent = math.ceil((Shop_Rent * Days_Occupied)/30)
        UtilityCharges = FinalAmount - Shop_Rent - BalanceDue if ID != 'MILL' else FinalAmount - Shop_Rent
        ClosingReading = round(Data[1], 1)
        OpeningReading = round(Data[2], 1)
        RawClosingDate = Data[3]
        ClosingDate = datetime.date.strftime(RawClosingDate, r'%d/%m/%Y')
        UnitsConsumed = round(ClosingReading - OpeningReading, 1)

        cursor.execute(f"SELECT DISTINCT [Closing Date] FROM [Monthly Report Data] WHERE [For The Month Of] = '{PreviousMonth}'")
        RawData = cursor.fetchone()
        RawOpeningDate = RawData[0] if RawData != None else '----------'
        OpeningDate = datetime.date.strftime(RawOpeningDate, r'%d/%m/%Y') if RawOpeningDate != '----------' else '----------'

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

        FinalAmount_Position1 = (380 + (135 - FinalAmountText_Width), 577)
        ShopID_Position = (832 + (104 - ShopIDText_Width)/2, 577)
        MonthAndTenantName_Position = (145, 648)
        ClosingReading_Position = (1482, 778)
        OpeningReading_Position = (1482, 851)
        UnitsConsumed_Position = (1482, 925)
        RoomRent_Position = (577, 778)
        UtilityCharges_Position = (577, 851)        
        FinalAmount_Position2 = (577, 925)
        ReceiptNumber_Position = (358, 339)
        Date_Position = (1909 + (239 - Date_Width), 339)

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

        Description_Size, Description_Colour = 42, (0, 0, 0)
        Description_Font = ImageFont.truetype('CalibriFont Regular.ttf', Description_Size)
        Date_Size, Date_Colour = 38, (0, 0, 0)
        Date_Font = ImageFont.truetype('CalibriFont Regular.ttf', Date_Size)
        ReceiptNumber_Size, ReceiptNumber_Colour = 38, (0, 0, 0)
        ReceiptNumber_Font = ImageFont.truetype('CalibriFont Bold.ttf', ReceiptNumber_Size)

        Draw = ImageDraw.Draw(Template)
        FinalAmountText_Width = Draw.textlength(str(FinalAmount), font=Description_Font)
        ShopIDText_Width = Draw.textlength(ID, font=Description_Font)
        Date_Width = Draw.textlength(Date, Description_Font)

        FinalAmount_Position = (372 + (104 - FinalAmountText_Width), 512)
        ShopID_Position = (758 + (72 - ShopIDText_Width)/2, 512)
        MonthAndTenantName_Position = (258, 567)
        ReceiptNumber_Position = (284, 307)
        Date_Position = (864 + (180 - Date_Width), 307)

        Draw.text(FinalAmount_Position, str(FinalAmount), Description_Colour, Description_Font)
        Draw.text(ShopID_Position, ID, Description_Colour, Description_Font)
        Draw.text(MonthAndTenantName_Position, f"{Month.capitalize()}-{Year[-2:]} From {TenantName}.", Description_Colour, Description_Font)
        Draw.text(ReceiptNumber_Position, str(ReceiptNumber), ReceiptNumber_Colour, ReceiptNumber_Font)
        Draw.text(Date_Position, Date, Date_Colour, Date_Font)

        Template.save(rf'Rent Receipts\Shop {ReceiptNumber}_{TenantName}-2.jpg', dpi = (300, 300))

        print(f"\nRent Receipts generated for '{TenantName}'.") 
        PrintSetup_SHOP_1(ReceiptNumber, TenantName)
        PrintSetup_SHOP_2(ReceiptNumber, TenantName)
    print('\n<<<<<<<<<<+>>>>>>>>>>\n')


# OTHER FUNCTIONS
def PrintSetup_ROOM(ReceiptNumber, TenantName):
    Receipt_1 = Image.open(rf"Rent Receipts\Room {ReceiptNumber}_{TenantName}-1.jpg")
    Receipt_2 = Image.open(rf"Rent Receipts\Room {ReceiptNumber}_{TenantName}-2.jpg")

    PrintSetup = Image.new('RGB', (1248, 2244), (255, 255, 255))

    PrintSetup.paste(Receipt_1, (0, 0))
    PrintSetup.paste(Receipt_2, (0, Receipt_1.height))

    OutputPath = rf"Final Print/Room {ReceiptNumber}_{TenantName}.pdf"
    PrintSetup.save(OutputPath, dpi = (300, 300))

    Drive = CopyReceipt_To_ExternalDrive(OutputPath)
    if Drive != None:
        print(f">> Successfully Copied To The External Removable Drive '{Drive}' <<")

def PrintSetup_SHOP_1(ReceiptNumber, TenantName):
    Receipt = Image.open(rf"Rent Receipts\Shop {ReceiptNumber}_{TenantName}-1.jpg")

    PrintSetup = Image.new('RGB', (2244, 1535), (255, 255, 255))

    PrintSetup.paste(Receipt, (0, 0))

    OutputPath = rf"Final Print/Shop {ReceiptNumber}_{TenantName}-1.pdf"
    PrintSetup.save(OutputPath, dpi = (300, 300))

    CopyReceipt_To_ExternalDrive(OutputPath)

def PrintSetup_SHOP_2(ReceiptNumber, TenantName):
    Receipt = Image.open(rf"Rent Receipts\Shop {ReceiptNumber}_{TenantName}-2.jpg")

    PrintSetup = Image.new('RGB', (1122, 1535), (255, 255, 255))

    PrintSetup.paste(Receipt, (0, 0))

    OutputPath = rf"Final Print/Shop {ReceiptNumber}_{TenantName}-2.pdf"
    PrintSetup.save(OutputPath, dpi = (300, 300))

    Drive = CopyReceipt_To_ExternalDrive(OutputPath)
    if Drive != None:
        print(f">> Successfully Copied To The External Removable Drive '{Drive}' <<")


def CopyReceipt_To_ExternalDrive(SourceFile):
    global ChosenDrive
    if ChosenDrive == '':
        AvailableDrives = [chr(i) + ':' for i in range(65, 91) if os.path.exists(chr(i) + ':')]
        AvailableRemovableDrives = [Drive for Drive in AvailableDrives if win32file.GetDriveType(Drive) == win32file.DRIVE_REMOVABLE]

        if len(AvailableRemovableDrives) == 1:
            TargetDIR = os.path.join(AvailableRemovableDrives[0], 'Rent Receipt Final Print')
            os.makedirs(TargetDIR, exist_ok=True)
            shutil.copy(SourceFile, TargetDIR)
            return AvailableRemovableDrives[0]
        elif len(AvailableRemovableDrives) != 0:
            print('\n', '-' * 75, sep='')
            print(f"{len(AvailableRemovableDrives)} Removable Drives FOUND, Choose One From The List Below")
            print('  (', end='')
            for Drive in AvailableRemovableDrives:
                print(Drive, end=', ') if Drive != AvailableRemovableDrives[-1] else print(Drive + ')')
            print('-' * 75, '\n', sep='')

            while True:
                ChosenDrive = input('Enter The Desired Drive: ').strip().upper()
                if ChosenDrive.endswith(':') and len(ChosenDrive) == 2 and ChosenDrive[0] in AvailableRemovableDrives:
                    break
                elif len(ChosenDrive) == 1 and (ChosenDrive + ':') in AvailableRemovableDrives:
                    ChosenDrive += ':'
                    break
                else:
                    print('INVALID Drive Chosen, TRY AGAIN...\n')

            TargetDIR = os.path.join(ChosenDrive, 'Rent Receipt Final Print')
            os.makedirs(TargetDIR, exist_ok=True)
            shutil.copy(SourceFile, TargetDIR)
            return ChosenDrive
        else:
            return None
    else:                
        TargetDIR = os.path.join(ChosenDrive, 'Rent Receipt Final Print')
        os.makedirs(TargetDIR, exist_ok=True)
        shutil.copy(SourceFile, TargetDIR)
        return ChosenDrive
