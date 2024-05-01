import datetime, calendar, math
import os, shutil
import win32file
from PIL import Image, ImageDraw, ImageFont

from CustomModules.VariablesModule import *
from CustomModules.EstablishConnection import *
from CustomModules.FetchDataModule import *

Today = datetime.date.today()
Date = Today.strftime(r'%d/%m/%Y')


# GENERATE RENT RECEIPT
def GenerateRoomRentReceipt_ALL():
    PreviousMonth, Month, PenultimateMonth, DatePreference = GetMonth(['WITHOUT MONTH'])
    LDate = Date[-5:] if DatePreference == 'WITHOUT MONTH' else Date[-8:]
    
    print('\n<<<<<<<<<<+>>>>>>>>>>')
    cursor.execute(f"SELECT [Tenant ID], [Year (YYYY)], [Tenant Name], [Room/Shop ID], [Receipt Number], [Individual Rent] \
                     FROM [Payment Details] WHERE [Status] = 'UNPAID' AND [For The Month Of] = '{Month}';")
    Records = cursor.fetchall()
    for Record in Records:
        TenantID, Year, TenantName, ID, ReceiptNumber = Record[:5]
        FinalAmount= int(Record[5])

        if ID not in Room_IDs:
            print('\n', '-' * 50, sep='')
            print(f"'{ID}' Is not a ROOM, So Receipt Generation SKIPPED...")
            print('-' * 50, '\n', sep='')
            continue

        cursor.execute(f"SELECT [Tenant Count], [Rent-1], [Rent-2], [Rent-3] FROM [Room/Shop Data] WHERE [Room/Shop ID] = '{ID}';")
        Data = cursor.fetchone()
        TenantCount = Data[0] if Month == PenultimateMonth else GetMonth(ID)
        Room_Rent = math.ceil((Data[TenantCount])/TenantCount) if TenantCount != 0 else 0

        BalanceDUE = GetBalanceDUE(TenantID, ID, PreviousMonth)

        cursor.execute(f"SELECT [Number Of Days Occupied], [Closing Sub-Meter Reading], [Opening Sub-Meter Reading] FROM [Monthly report Data] \
                         WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
        Data = cursor.fetchone()
        Days_Occupied = Data[0]
        Room_Rent = math.ceil((Room_Rent * Days_Occupied)/30)
        ClosingReading, OpeningReading = round(Data[1], 1), round(Data[2], 1)

        GenerateRoomRentReceipt(LDate, FinalAmount, ID, Month, Year, TenantName, ClosingReading, OpeningReading, Room_Rent, BalanceDUE, ReceiptNumber)
    print('\n<<<<<<<<<<+>>>>>>>>>>\n')

def GenerateRoomRentReceipt_SPECIFIC(Month = None, ReceiptNumber_List = None):
    PreviousMonth, Month, _, DatePreference = GetMonth(['WITHOUT DATE', 'WITHOUT MONTH'], Month)
    LDate = Date[-8:] if DatePreference == 'WITHOUT DATE' else Date[-5:] if DatePreference == 'WITHOUT MONTH' else Date

    if ReceiptNumber_List is None:
        while True:
            IsRunning, ReceiptNumber_List = GenerateList('Receipt NOs (eg. 11-22, 33)')
            if not IsRunning:
                if ReceiptNumber_List[0] == 'FIND RECEIPT NUMBER':
                    GetReceiptNumber(Month)
                    return GenerateRoomRentReceipt_SPECIFIC(Month)

                cursor.execute(f"""
                                 SELECT [Receipt Number] FROM [Payment Details] WHERE [For The Month OF] = '{Month}'
                                 UNION
                                 SELECT [Receipt Number] FROM [Payment Details (NS)] WHERE [For The Month OF] = '{Month}';
                """)
                RawData = cursor.fetchall()
                ValidReceiptNumbers = [str(ReceiptNumber[0]) for ReceiptNumber in RawData]
                if all(ReceiptNumber in ValidReceiptNumbers for ReceiptNumber in ReceiptNumber_List):
                    break
                else:
                    print('Some Receipt Numbers Are NOT VALID, Try Again...')

    print('\n<<<<<<<<<<+>>>>>>>>>>')
    for ReceiptNumber in ReceiptNumber_List:
        cursor.execute(f"SELECT [Individual Rent], [Year (YYYY)], [Tenant ID], [Tenant Name], [Room/Shop ID] FROM [Payment Details] WHERE [Receipt Number] = {ReceiptNumber};")
        Record = cursor.fetchone()
        RNO_Type = 'Standard'
        if Record is None:
            cursor.execute(f"SELECT [Individual Rent], [Year (YYYY)], [Tenant ID], [Tenant Name], [Room/Shop ID] FROM [Payment Details (NS)] \
                        WHERE [Receipt Number] = {ReceiptNumber};")
            Record = cursor.fetchone()
            RNO_Type = 'Non-Standard'
        Year, TenantID, TenantName, ID = Record[1:]
        FinalAmount= int(Record[0])

        if ID not in Room_IDs:
            print('\n', '-' * 50, sep='')
            print(f"'{ID}' Is not a ROOM, So Receipt Generation SKIPPED...")
            print('-' * 50, '\n', sep='')
            continue

        cursor.execute(f"SELECT [Tenant Count], [Rent-1], [Rent-2], [Rent-3] FROM [Room/Shop Data] WHERE [Room/Shop ID] = '{ID}'")
        Data = cursor.fetchone()
        TenantCount = Data[0] if Month.capitalize() in [calendar.month_name[Today.month-1], calendar.month_name[Today.month]] else GetTenantCount(ID)
        Room_Rent = math.ceil((Data[TenantCount])/TenantCount) if TenantCount != 0 else 0

        BalanceDUE = GetBalanceDUE(TenantID, ID, PreviousMonth)

        if RNO_Type == 'Standard':
            cursor.execute(f"SELECT [Number Of Days Occupied], [Closing Sub-Meter Reading], [Opening Sub-Meter Reading] FROM [Monthly report Data] \
                WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
        elif RNO_Type == 'Non-Standard':
            cursor.execute(f"SELECT [Number Of Days Occupied], [Closing Sub-Meter Reading], [Opening Sub-Meter Reading] FROM [Unusual Occupancy Details] \
                WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
        Data = cursor.fetchone()
        Days_Occupied = Data[0]
        Room_Rent = math.ceil((Room_Rent * Days_Occupied)/30)
        ClosingReading, OpeningReading = round(Data[1], 1), round(Data[2], 1)

        GenerateRoomRentReceipt(LDate, FinalAmount, ID, Month, Year, TenantName, ClosingReading, OpeningReading, Room_Rent, BalanceDUE, ReceiptNumber)
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

def GenerateRoomRentReceipt_EXPECT(Month = None, ReceiptNumber_List = None):
    PreviousMonth, Month, PenultimateMonth, DatePreference = GetMonth(['WITHOUT MONTH'], Month)
    LDate = Date[-5:] if DatePreference == 'WITHOUT MONTH' else Date[-8:]

    if ReceiptNumber_List is None:
        while True:
            IsRunning, ReceiptNumber_List = GenerateList('Receipt NOs (eg. 11-22, 33)')
            if not IsRunning:
                if ReceiptNumber_List[0] == 'FIND RECEIPT NUMBER':
                    GetReceiptNumber(Month)
                    return GenerateRoomRentReceipt_SPECIFIC(Month)

                cursor.execute(f"""
                                 SELECT [Receipt Number] FROM [Payment Details] WHERE [For The Month OF] = '{Month}'
                                 UNION
                                 SELECT [Receipt Number] FROM [Payment Details (NS)] WHERE [For The Month OF] = '{Month}';
                """)
                RawData = cursor.fetchall()
                ValidReceiptNumbers = [str(ReceiptNumber) for ReceiptNumber, in RawData]
                if all(ReceiptNumber in ValidReceiptNumbers for ReceiptNumber in ReceiptNumber_List):
                    ReceiptNumber_List = [int(ReceiptNumber) for ReceiptNumber in ReceiptNumber_List]
                    break
                else:
                    print('Some Receipt Numbers Are NOT VALID, Try Again...')

    print('\n<<<<<<<<<<+>>>>>>>>>>')
    cursor.execute(f"SELECT [Tenant ID], [Year (YYYY)], [Tenant Name], [Room/Shop ID], [Receipt Number], [Individual Rent] \
                     FROM [Payment Details] WHERE [Status] = 'UNPAID' AND [For The Month Of] = '{Month}';")
    Records = cursor.fetchall()
    for Record in Records:
        TenantID, Year, TenantName, ID, ReceiptNumber = Record[:5]
        FinalAmount= int(Record[5])

        if ReceiptNumber in ReceiptNumber_List:
            continue
        if ID not in Room_IDs:
            print('\n', '-' * 50, sep='')
            print(f"'{ID}' Is not a ROOM, So Receipt Generation SKIPPED...")
            print('-' * 50, '\n', sep='')
            continue

        cursor.execute(f"SELECT [Tenant Count], [Rent-1], [Rent-2], [Rent-3] FROM [Room/Shop Data] WHERE [Room/Shop ID] = '{ID}';")
        Data = cursor.fetchone()
        TenantCount = Data[0] if Month == PenultimateMonth else GetMonth(ID)
        Room_Rent = math.ceil((Data[TenantCount])/TenantCount) if TenantCount != 0 else 0

        BalanceDUE = GetBalanceDUE(TenantID, ID, PreviousMonth)

        cursor.execute(f"SELECT [Number Of Days Occupied], [Closing Sub-Meter Reading], [Opening Sub-Meter Reading] FROM [Monthly report Data] \
                         WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
        Data = cursor.fetchone()
        Days_Occupied = Data[0]
        Room_Rent = math.ceil((Room_Rent * Days_Occupied)/30)
        ClosingReading, OpeningReading = round(Data[1], 1), round(Data[2], 1)

        GenerateRoomRentReceipt(LDate, FinalAmount, ID, Month, Year, TenantName, ClosingReading, OpeningReading, Room_Rent, BalanceDUE, ReceiptNumber)
    print('\n<<<<<<<<<<+>>>>>>>>>>\n')

def GenerateShopRentReceipt_ALL():
    PreviousMonth, Month, _, DatePreference = GetMonth(['WITHOUT MONTH'])
    LDate = Date[-5:] if DatePreference == 'WITHOUT MONTH' else Date[-8:]

    print('\n<<<<<<<<<<+>>>>>>>>>>')
    cursor.execute(f"SELECT [Tenant ID], [Year (YYYY)], [Tenant Name], [Room/Shop ID], [Receipt Number], [Individual Rent] \
                     FROM [Payment Details] WHERE [Status] = 'UNPAID' AND [For The Month Of] = '{Month}';")
    Records = cursor.fetchall()
    for Record in Records:
        TenantID, Year, TenantName, ID, ReceiptNumber = Record[:5]
        FinalAmount= int(Record[5])

        cursor.execute(f"SELECT [Shop Name (Optional)] FROM [Occupancy Information] WHERE [Room/Shop ID] = '{ID}' AND [Tenant ID] = '{TenantID}';")
        ShopName = cursor.fetchone()[0]

        if ID not in Shop_IDs:
            print('\n', '-' * 50, sep='')
            print(f"'{ID}' Is not a Shop, So Receipt Generation SKIPPED...")
            print('-' * 50, '\n', sep='')
            continue

        cursor.execute(f"SELECT [Rent-1] FROM [Room/Shop Data] WHERE [Room/Shop ID] = '{ID}'")
        Shop_Rent = cursor.fetchone()[0]

        BalanceDUE = GetBalanceDUE(TenantID, ID, PreviousMonth)

        cursor.execute(f"SELECT [Number Of Days Occupied], [Closing Sub-Meter Reading], [Opening Sub-Meter Reading], [Closing Date] \
                       FROM [Monthly report Data] WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
        Data = cursor.fetchone()
        Days_Occupied = Data[0]
        Shop_Rent = math.ceil((Shop_Rent * Days_Occupied)/30)
        ClosingReading,OpeningReading = round(Data[1], 1), round(Data[2], 1)
        ClosingDate = datetime.date.strftime(Data[3], r'%d/%m/%Y')
        OpeningDate = GetOpeningDate(Month, PreviousMonth, ID)

        GenerateShopRentReceipt(LDate, FinalAmount, ID, Month, Year, TenantName, ClosingReading, OpeningReading, Shop_Rent, BalanceDUE, ReceiptNumber, ShopName, ClosingDate, OpeningDate)
    print('\n<<<<<<<<<<+>>>>>>>>>>\n')

def GenerateShopRentReceipt_SPECIFIC(Month = None, ReceiptNumber_List = None):
    PreviousMonth, Month, _, DatePreference = GetMonth(['WITHOUT DATE', 'WITHOUT MONTH'], Month)
    LDate = Date[-8:] if DatePreference == 'WITHOUT DATE' else Date[-5:] if DatePreference == 'WITHOUT MONTH' else Date

    if ReceiptNumber_List is None:
        while True:
            IsRunning, ReceiptNumber_List = GenerateList('Receipt NOs (eg. 11-22, 33)')
            if not IsRunning:
                if ReceiptNumber_List[0] == 'FIND RECEIPT NUMBER':
                    GetReceiptNumber(Month)
                    return GenerateRoomRentReceipt_SPECIFIC(Month)

                cursor.execute(f"""
                                 SELECT [Receipt Number] FROM [Payment Details] WHERE [For The Month OF] = '{Month}'
                                 UNION
                                 SELECT [Receipt Number] FROM [Payment Details (NS)] WHERE [For The Month OF] = '{Month}';
                """)
                RawData = cursor.fetchall()
                ValidReceiptNumbers = [str(ReceiptNumber[0]) for ReceiptNumber in RawData]
                if all(ReceiptNumber in ValidReceiptNumbers for ReceiptNumber in ReceiptNumber_List):
                    break
                else:
                    print('Some Receipt Numbers Are NOT VALID, Try Again...')

    print('\n<<<<<<<<<<+>>>>>>>>>>')
    for ReceiptNumber in ReceiptNumber_List:
        cursor.execute(f"SELECT [Individual Rent], [Year (YYYY)], [Tenant ID], [Tenant Name], [Room/Shop ID] FROM [Payment Details] WHERE [Receipt Number] = {ReceiptNumber};")
        Record = cursor.fetchone()
        RNO_Type = 'Standard'
        if Record is None:
            cursor.execute(f"SELECT [Individual Rent], [Year (YYYY)], [Tenant ID], [Tenant Name], [Room/Shop ID] FROM [Payment Details (NS)] \
                        WHERE [Receipt Number] = {ReceiptNumber};")
            Record = cursor.fetchone()
            RNO_Type = 'Non-Standard'
        Year, TenantID, TenantName, ID = Record[1:]
        FinalAmount= int(Record[0])

        cursor.execute(f"SELECT [Shop Name (Optional)] FROM [Occupancy Information] WHERE [Room/Shop ID] = '{ID}' AND [Tenant ID] = '{TenantID}'")
        ShopName = cursor.fetchone()[0]

        if ID not in Shop_IDs:
            print('\n', '-' * 50, sep='')
            print(f"'{ID}' Is not a SHOP, So Receipt Generation SKIPPED...")
            print('-' * 50, '\n', sep='')
            continue

        cursor.execute(f"SELECT [Rent-1] FROM [Room/Shop Data] WHERE [Room/Shop ID] = '{ID}'")
        Shop_Rent = cursor.fetchone()[0]

        BalanceDUE = GetBalanceDUE(TenantID, ID, PreviousMonth)

        if RNO_Type == 'Standard':
            cursor.execute(f"SELECT [Number Of Days Occupied], [Closing Sub-Meter Reading], [Opening Sub-Meter Reading], [Closing Date] FROM [Monthly report Data] \
                WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
        elif RNO_Type == 'Non-Standard':
            cursor.execute(f"SELECT [Number Of Days Occupied], [Closing Sub-Meter Reading], [Opening Sub-Meter Reading], [Closing Date] FROM [Unusual Occupancy Details] \
                WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
        Data = cursor.fetchone()
        Days_Occupied = Data[0]
        Shop_Rent = math.ceil((Shop_Rent * Days_Occupied)/30)
        ClosingReading, OpeningReading = round(Data[1], 1), round(Data[2], 1)
        ClosingDate = datetime.date.strftime(Data[3], r'%d/%m/%Y')
        OpeningDate = GetOpeningDate(Month, PreviousMonth, ID)

        GenerateShopRentReceipt(LDate, FinalAmount, ID, Month, Year, TenantName, ClosingReading, OpeningReading, Shop_Rent, BalanceDUE, ReceiptNumber, ShopName, ClosingDate, OpeningDate)
    print('\n<<<<<<<<<<+>>>>>>>>>>\n')

def GenerateShopRentReceipt_EXPECT(Month = None, ReceiptNumber_List = None):
    PreviousMonth, Month, _, DatePreference = GetMonth(['WITHOUT MONTH'], Month)
    LDate = Date[-5:] if DatePreference == 'WITHOUT MONTH' else Date[-8:]

    if ReceiptNumber_List is None:
        while True:
            IsRunning, ReceiptNumber_List = GenerateList('Receipt NOs (eg. 11-22, 33)')
            if not IsRunning:
                if ReceiptNumber_List[0] == 'FIND RECEIPT NUMBER':
                    GetReceiptNumber(Month)
                    return GenerateRoomRentReceipt_SPECIFIC(Month)

                cursor.execute(f"""
                                 SELECT [Receipt Number] FROM [Payment Details] WHERE [For The Month OF] = '{Month}'
                                 UNION
                                 SELECT [Receipt Number] FROM [Payment Details (NS)] WHERE [For The Month OF] = '{Month}';
                """)
                RawData = cursor.fetchall()
                ValidReceiptNumbers = [str(ReceiptNumber) for ReceiptNumber, in RawData]
                if all(ReceiptNumber in ValidReceiptNumbers for ReceiptNumber in ReceiptNumber_List):
                    ReceiptNumber_List = [int(ReceiptNumber) for ReceiptNumber in ReceiptNumber_List]
                    break
                else:
                    print('Some Receipt Numbers Are NOT VALID, Try Again...')

    print('\n<<<<<<<<<<+>>>>>>>>>>')
    cursor.execute(f"SELECT [Tenant ID], [Year (YYYY)], [Tenant Name], [Room/Shop ID], [Receipt Number], [Individual Rent] \
                     FROM [Payment Details] WHERE [Status] = 'UNPAID' AND [For The Month Of] = '{Month}';")
    Records = cursor.fetchall()
    for Record in Records:
        TenantID, Year, TenantName, ID, ReceiptNumber = Record[:5]
        FinalAmount= int(Record[5])

        cursor.execute(f"SELECT [Shop Name (Optional)] FROM [Occupancy Information] WHERE [Room/Shop ID] = '{ID}' AND [Tenant ID] = '{TenantID}'")
        ShopName = cursor.fetchone()[0]

        if ReceiptNumber in ReceiptNumber_List:
            continue
        if ID not in Shop_IDs:
            print('\n', '-' * 50, sep='')
            print(f"'{ID}' Is not a Shop, So Receipt Generation SKIPPED...")
            print('-' * 50, '\n', sep='')
            continue

        cursor.execute(f"SELECT [Rent-1] FROM [Room/Shop Data] WHERE [Room/Shop ID] = '{ID}'")
        Shop_Rent = cursor.fetchone()[0]

        BalanceDUE = GetBalanceDUE(TenantID, ID, PreviousMonth)

        cursor.execute(f"SELECT [Number Of Days Occupied], [Closing Sub-Meter Reading], [Opening Sub-Meter Reading], [Closing Date] \
                       FROM [Monthly report Data] WHERE [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{Month}';")
        Data = cursor.fetchone()
        Days_Occupied = Data[0]
        Shop_Rent = math.ceil((Shop_Rent * Days_Occupied)/30)
        ClosingReading, OpeningReading = round(Data[1], 1), round(Data[2], 1)
        ClosingDate = datetime.date.strftime(Data[3], r'%d/%m/%Y')
        OpeningDate = GetOpeningDate(Month, PreviousMonth, ID)

        GenerateShopRentReceipt(LDate, FinalAmount, ID, Month, Year, TenantName, ClosingReading, OpeningReading, Shop_Rent, BalanceDUE, ReceiptNumber, ShopName, ClosingDate, OpeningDate)
    print('\n<<<<<<<<<<+>>>>>>>>>>\n')



# OTHER FUNCTIONS
def GenerateRoomRentReceipt(Date, FinalAmount: int, ID: str, Month: str, Year: str, TenantName: str, ClosingReading: float, OpeningReading:float, Room_Rent: int, \
                            BalanceDUE: int, ReceiptNumber: int | str) -> None:
    UtilityCharges = FinalAmount - Room_Rent - BalanceDUE
    UnitsConsumed = round(ClosingReading - OpeningReading, 1)

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

    FinalAmount_Position1 = (459 + (126 - FinalAmountText_Width), 532)
    RoomID_Position = (925 + (73 - RoomIDText_Width)/2, 532)
    MonthAndTenantName_Position = (291, 598)
    ClosingReading_Position = (675, 707)
    OpeningReading_Position = (675, 771)
    UnitsConsumed_Position = (675, 834)
    RoomRent_Position = (675, 898)
    UtilityCharges_Position = (675, 959)        
    FinalAmount_Position2 = (675, 1023)
    ReceiptNumber_Position = (337, 305)
    Date_Position = (913 + (217 - Date_Width), 305)

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

def GenerateShopRentReceipt(Date, FinalAmount: int, ID: str, Month: str, Year: str, TenantName: str, ClosingReading: float, OpeningReading:float, Shop_Rent: int, \
                            BalanceDUE: int, ReceiptNumber: int | str, ShopName: str, ClosingDate: str, OpeningDate: str) -> None:
    Today = datetime.date.today()

    UtilityCharges = FinalAmount - Shop_Rent - BalanceDUE if ID != 'MILL' else FinalAmount - Shop_Rent
    UnitsConsumed = round(ClosingReading - OpeningReading, 1)

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
    if ShopName is None:
        Draw.text(MonthAndTenantName_Position, f"{Month.capitalize()}, {Year} From Mr./Mrs. {TenantName}.", Description_Colour, Description_Font)
    else:
        Draw.text(MonthAndTenantName_Position, f"{Month.capitalize()}, {Year} From Mr./Mrs. {TenantName} ({ShopName}).", Description_Colour, Description_Font)
    Draw.text(ClosingReading_Position, f"{ClosingReading}    ({ClosingDate})", Data_Colour, Data_Font)
    Draw.text(OpeningReading_Position, f"{OpeningReading}    ({OpeningDate})", Data_Colour, Data_Font)
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
    if ChosenDrive is not None:
        return CopyAction(ChosenDrive, SourceFile)

    AvailableDrives = [
        f'{chr(i)}:' for i in range(65, 91) if os.path.exists(f'{chr(i)}:')
    ]
    AvailableRemovableDrives = [Drive for Drive in AvailableDrives if win32file.GetDriveType(Drive) == win32file.DRIVE_REMOVABLE]

    if len(AvailableRemovableDrives) == 1:
        return CopyAction(AvailableRemovableDrives[0], SourceFile)
    elif len(AvailableRemovableDrives) != 0:
        return GetDrive(AvailableRemovableDrives, ChosenDrive, SourceFile)
    else:
        return None


def GetMonth(AvailablePreferences: list, Month = None):
    if Month is None:
        DatePreference = None
        while True:
            Month = input('\nEnter The Desired Month (eg. JAN or JANUARY): ').strip().upper()
            if DatePreference is None and Month in AvailablePreferences:
                DatePreference = Month
                print('Preference ACCEPTED...')
            Month = calendar.month_name[Today.month-1].upper() if Month == '' else Month
            Month = MonthNames[Month] if Month in MonthNames.keys() else Month
            Month = Month if Month in MonthNames.values() else Month
            if Month not in MonthNames.values():
                print('INVALID Month Name, TRY AGAIN...')
                continue
            break
    else:
        DatePreference = GetPreference(AvailablePreferences)

    PreviousMonth = list(MonthNames.values())[(list(MonthNames.values()).index(Month))-1]
    PenultimateMonth = calendar.month_name[Today.month-1].upper()
    return PreviousMonth, Month, PenultimateMonth, DatePreference

def GetPreference(AvailablePreferences: list):
    while True:
        RawData = input('Enter Your Preference (OPTIONAL): ').strip().upper()
        if RawData in AvailablePreferences:
            DatePreference = RawData
            print('Preference ACCEPTED...')
            return DatePreference
        elif RawData == '':
            return None
        # DatePreference = 'Without Date' if RawData.upper() ==  else 'Without Month' \
        #                                 if RawData.upper() ==  else ''
        else:
            print('INVALID Entry, TRY AGAIN...')

def GetBalanceDUE(TenantID, ID, PreviousMonth):
    cursor.execute(f"SELECT [DUE Amount] FROM [DUE Details] WHERE [Tenant ID] = '{TenantID}' AND [Room/Shop ID] = '{ID}' AND [For The Month Of] = '{PreviousMonth}';")
    RawData = cursor.fetchone()
    return int(RawData[0]) if RawData != None else 0

def GetOpeningDate(Month, PreviousMonth, ID):
    cursor.execute(f"SELECT [Closing Date] FROM [Unusual Occupancy Details] WHERE [For The Month Of] = '{Month}' AND [Room/Shop ID] = '{ID}'")
    RawData = cursor.fetchall()
    if RawData != []:
        DateOBJs = [datetime.datetime.strptime(str(Record[0])[:10], r'%Y-%m-%d') for Record in RawData]
        OpeningDate = datetime.date.strftime(max(DateOBJs), r'%d/%m/%Y')
    else:
        cursor.execute(f"SELECT [Closing Date] FROM [Monthly Report Data] WHERE [For The Month Of] = '{PreviousMonth}' AND [Room/Shop ID] = '{ID}'")
        RawData = cursor.fetchone()
        OpeningDate = datetime.date.strftime(RawData[0], r'%d/%m/%Y') if RawData != None else '---------------'
    return OpeningDate

def GenerateList(WhatToGet):
    Elements = input(f'\nEnter The {WhatToGet}: ').upper()
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

            List.extend([str(_) for _ in range(Start, End+1)])
        else:
            List.append(i)
    return False, List

def GetTenantCount(ID):
    while True:
        TenantCount = input(f'\nEnter Tenant Count For The Room/Shop (ID: {ID}): ')
        if TenantCount in ['1', '2', '3']:
            return int(TenantCount)
        else:
            print('INVALID Tenant Count, TRY AGAIN...')

def GetReceiptNumber(Month):
    print("\n\n---- ENTER 'STOP' TO QUIT ----")
    print('\n<<<<<+>>>>>')
    while True:
        TenantName = input('\nEnter The Tenant Name To Receipt Number(s): ').strip().upper()
        if TenantName == 'STOP':
            break
        Records = FetchData_TenantID_FROM_TenantName(False, TenantName)
        if Records is not None:
            for Record in Records:
                Data = FetchData_ReceiptNumber_FROM_TenantID(False, Record[0], Month)
                if Data is not None:
                    print(f"\n>> The Receipt Number(s) Correspond To The Tenant (ID: {Record[0]}; Name: {Record[1]}) Is(Are):")
                    for i, (ReceiptNumber, Status) in enumerate(Data):
                        print(f"  {i+1}) {ReceiptNumber}  (Status: {Status})")
        print()
    print('\n<<<<<+>>>>>')


def GetDrive(AvailableRemovableDrives, ChosenDrive, SourceFile):
    print('\n', '-' * 75, sep='')
    print(f"{len(AvailableRemovableDrives)} Removable Drives FOUND, Choose One From The List Below")

    print('  (', end='')
    for Drive in AvailableRemovableDrives:
        print(Drive, end=', ') if Drive != AvailableRemovableDrives[-1] else print(f'{Drive})')

    print('-' * 75, '\n', sep='')

    while True:
        ChosenDrive = input('\nEnter The Desired Drive: ').strip().upper()
        if ChosenDrive.endswith(':') and len(ChosenDrive) == 2 and ChosenDrive[0] in AvailableRemovableDrives:
            break
        elif len(ChosenDrive) == 1 and f'{ChosenDrive}:' in AvailableRemovableDrives:
            ChosenDrive += ':'
            break
        else:
            print('INVALID Drive Chosen, TRY AGAIN...')

    return CopyAction(ChosenDrive, SourceFile)

def CopyAction(ChosenDrive, SourceFile):
    TargetDIR = os.path.join(ChosenDrive, 'Rent Receipt Final Print')
    os.makedirs(TargetDIR, exist_ok=True)
    shutil.copy(SourceFile, TargetDIR)
    return ChosenDrive


__all__ = ['GenerateRoomRentReceipt_ALL', 'GenerateRoomRentReceipt_SPECIFIC', 'GenerateRoomRentReceipt_EXPECT', 'GenerateShopRentReceipt_ALL', 'GenerateShopRentReceipt_SPECIFIC', 'GenerateShopRentReceipt_EXPECT']