import time
import os, sys

from CustomModules.EstablishConnection import *
from CustomModules.UpdateModule import *
from CustomModules.VariablesModule import *
from CustomModules.GenerateRentReceiptModule import *
from CustomModules.FetchDataModule import *
from CustomModules.DuplicateRecordsModule import *
from CustomModules.CheckConsistencyModule import *
from CustomModules.CustomActionModule import *
from CustomModules.InsertDataModule import *



# Checking Basic Requirements
os.makedirs('Final Print', exist_ok=True)
os.makedirs('Rent Receipts', exist_ok=True)
if not(os.path.exists(r'Static Templates\Room Rent Receipt-1.jpg') and os.path.exists(r'Static Templates\Room Rent Receipt-2.jpg') and \
       os.path.exists(r'Static Templates\Shop Rent Receipt-1.jpg') and os.path.exists(r'Static Templates\Shop Rent Receipt-2.jpg') and \
       os.path.exists('CalibriFont Bold.ttf') and os.path.exists('CalibriFont Regular.ttf')): 
    print('\n', '-' * 80, sep='')
    print('Requirements NOT SATISFIED!! Some Files May Be Missing, TRY AGAIN...')
    print('-' * 80, '\n', sep='')
    time.sleep(3)
    sys.exit()  



def MAIN_MENU_FUNCTION():
    global ChosenDrive, ChosenPrinter
    ChosenDrive, ChosenPrinter = '', None

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
        print('\n', '-' * 50, sep='')
        print('User TRIGGERED Exit Command...')
        print('-' * 50, '\n', sep='')
        time.sleep(1)
        os.system('cls')
        sys.exit()  

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
                Update_ClosingReading_Field()

                print(f"'{SUB_MENU_UPDATE[User_Choice-1]}' Field UPDATED Successfully...")
                input('\nPress ENTER Key To Continue...')
                MAIN_MENU_FUNCTION()

            elif User_Choice == 8:
                Update_NumberOfDaysOccupied_Field()

                print(f"'{SUB_MENU_UPDATE[User_Choice-1]}' Field UPDATED Successfully...")
                input('\nPress ENTER Key To Continue...')
                MAIN_MENU_FUNCTION()

        # Calling SUB_MENU_UPDATE
        SUB_MENU_UPDATE_FUNCTION()                

    elif User_Choice == 3:
        def SUB_MENU_GENERATE_RENT_RECEIPT_FUNCTION():
            global ChosenPrinter

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
                    # print('\n<<<<<<<<<<+>>>>>>>>>>')
                    # UserPreference = input('Do You Want To Print The Receipt Simultaneously? (Y/N): ').strip().upper()
                    # if UserPreference == 'Y' or UserPreference == '':
                    #     ActivePrinters, IsPrinterAvailable = GETPrinters()
                    #     if IsPrinterAvailable:
                    #         ChosenPrinter = ChoosePrinter(ActivePrinters)
                    #     else:
                    #         print('\n>>> NO PRINTERS AVAILABLE <<<')

                    GenerateShopRentReceipt_ALL()

                    input('\nPress ENTER Key To Continue...')
                    MAIN_MENU_FUNCTION()

                elif User_Choice == 3:
                    # print('\n<<<<<<<<<<+>>>>>>>>>>')
                    # UserPreference = input('Do You Want To Print The Receipt Simultaneously? (Y/N): ').strip().upper()
                    # if UserPreference == 'Y' or UserPreference == '':
                    #     ActivePrinters, IsPrinterAvailable = GETPrinters()
                    #     if IsPrinterAvailable:
                    #         ChosenPrinter = ChoosePrinter(ActivePrinters)
                    #     else:
                    #         print('\n>>> NO PRINTERS AVAILABLE <<<')

                    GenerateShopRentReceipt_SPECIFIC()

                    input('\nPress ENTER Key To Continue...')
                    MAIN_MENU_FUNCTION()

        # Calling SUB_MENU_UPDATE
        SUB_MENU_GENERATE_RENT_RECEIPT_FUNCTION()                

    elif User_Choice == 4:
        print('\nSUB MENU (CHECK_FOR_CONSISTENCY):')
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

            input('\nPress ENTER Key To Continue...')
            MAIN_MENU_FUNCTION()
        
        elif User_Choice == 3:
            DuplicateRecords_DUEDetails()

            input('\nPress ENTER Key To Continue...')
            MAIN_MENU_FUNCTION()

        elif User_Choice == 4:
            DuplicateRecords_PaymentDetails()

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
            FetchData_TenantID_FROM_OccupiedSpaceID()

            input('\nPress ENTER Key To Continue...')
            MAIN_MENU_FUNCTION()

        elif User_Choice == 5:
            FetchData_ReceiptNumber_FROM_TenantID()

            input('\nPress ENTER Key To Continue...')
            MAIN_MENU_FUNCTION()

        elif User_Choice == 6:
            FetchData_UNPAID_Tenants()

            input('\nPress ENTER Key To Continue...')
            MAIN_MENU_FUNCTION()

        elif User_Choice == 7:
            FetchData_GetTenantDetails()

            input('\nPress ENTER Key To Continue...')
            MAIN_MENU_FUNCTION()

        elif User_Choice == 8:
            FetchDate_Vacancy()

            input('\nPress ENTER Key To Continue...')
            MAIN_MENU_FUNCTION()

        elif User_Choice == 9:
            FetchData_TotalCashReceived()

            input('\nPress ENTER Key To Continue...')
            MAIN_MENU_FUNCTION()

        elif User_Choice == 10:
            FetchData_UnitsConsumed()

            input('\nPress ENTER Key To Continue...')
            MAIN_MENU_FUNCTION()

    elif User_Choice == 7:
        print('\nSUB MENU (INSERT_DATA):')
        for i, Choice in enumerate(SUB_MENU_INSERT_DATA):
            print(f'{i+1})', Choice)    

        while True:
            User_Choice = input('Enter Your Choice ID: ')
            if User_Choice in [str(i+1) for i in range(len(SUB_MENU_INSERT_DATA))]:
                User_Choice = int(User_Choice)
                break
            else:
                print('ID Not Defined, TRY AGAIN...')

        if User_Choice == 1:
            MAIN_MENU_FUNCTION()

        elif User_Choice == 2:
            InsertData_WaterPurchaseDetails()

            input('\nPress ENTER Key To Continue...')
            MAIN_MENU_FUNCTION()

        elif User_Choice == 3:
            InsertData_UnusualDepartureDetails()

            input('\nPress ENTER Key To Continue...')
            MAIN_MENU_FUNCTION()

        elif User_Choice == 4:
            InsertData_PaymentDetailsNS()

            input('\nPress ENTER Key To Continue...')
            MAIN_MENU_FUNCTION()

    elif User_Choice == 8:
        print('\nSUB MENU (CUSTOM_ACTION):')
        for i, Choice in enumerate(SUB_MENU_CUSTOM_ACTION):
            print(f'{i+1})', Choice)    

        while True:
            User_Choice = input('Enter Your Choice ID: ')
            if User_Choice in [str(i+1) for i in range(len(SUB_MENU_CUSTOM_ACTION))]:
                User_Choice = int(User_Choice)
                break
            else:
                print('ID Not Defined, TRY AGAIN...')

        if User_Choice == 1:
            MAIN_MENU_FUNCTION()

        elif User_Choice == 2:
            CustomAction_MonthEndAction()

            input('\nPress ENTER Key To Continue...')
            MAIN_MENU_FUNCTION()

        elif User_Choice == 3:
            CustomAction_MonthBeginningAction()

            input('\nPress ENTER Key To Continue...')
            MAIN_MENU_FUNCTION()

        elif User_Choice == 4:
            CustomAction_UnusualDepartureAction()

            input('\nPress ENTER Key To Continue...')
            MAIN_MENU_FUNCTION()

# Calling MAIN_MENU
MAIN_MENU_FUNCTION()


# Close cursor and connection
cursor.close()
con.close()
