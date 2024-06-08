from CustomModules.EstablishConnection import *
from CustomModules.VariablesModule import *
from CustomModules.UpdateModule import *
from CustomModules.GenerateRentReceiptModule import *
from CustomModules.InsertDataModule import *
from CustomModules.DuplicateRecordsModule import *
from CustomModules.FetchDataModule import *
from CustomModules.SendNotificationModule import *

def CustomAction_MonthEndAction():
    DuplicateRecords_MonthlyReportData()
    Update_ClosingReading_Field()

    input('\nPress ENTER Key To UPDATE Days Occupied...')
    Update_DaysOccupied_Field()

def CustomAction_MonthBeginningAction():
    Update_TenantsCount_Field()

    Month = Update_TotalRent_Field(False)

    DuplicateRecords_PaymentDetails()
    Update_IndividualRent_Field(Month)

    Delete_DUEDetails()
    DuplicateRecords_DUEDetails()

    SendNotification_ALL()

def CustomAction_UnusualArrivalAction():
    ID, Date = InsertData_UnusualDepartureDetails()

    Month, ReceiptNumber_List, _ = InsertData_PaymentDetailsNS(ID, Date, False)

    if ID in Room_IDs:
        GenerateRoomRentReceipt_SPECIFIC(Month, ReceiptNumber_List)
    elif ID in Shop_IDs:
        GenerateShopRentReceipt_SPECIFIC(Month, ReceiptNumber_List)

    print('\n>> Follow Along To ADD NEW OCCUPANCY <<')
    CustomAction_NewOccupancyAction()

def CustomAction_UnusualDepartureAction():
    ID, Date = InsertData_UnusualDepartureDetails()
    Month, ReceiptNumber_List, VacatingTenant_List = InsertData_PaymentDetailsNS(ID, Date)

    for TenantID in VacatingTenant_List:
        cursor.execute(f"UPDATE [Occupancy Information] SET [To (Date)] = ? WHERE [Tenant ID] = '{TenantID}' AND [To (Date)] IS NULL;", (Date,))
        cursor.commit()

    Update_CurrentStatus_Field()

    if ID in Room_IDs:
        GenerateRoomRentReceipt_SPECIFIC(Month, ReceiptNumber_List)
    elif ID in Shop_IDs:
        GenerateShopRentReceipt_SPECIFIC(Month, ReceiptNumber_List)

def CustomAction_NewOccupancyAction():
    while True:
        ANS = input("\nDo You Want To Add Tenant's Information (Y/N): ").strip().upper()
        if ANS in ['Y', '']:
            TenantID, Date = InsertData_TenantsInformation()
            InsertData_OccupancyInformation(TenantID, Date)
            break
        elif ANS in ['N']:
            TenantID = InsertData_OccupancyInformation()

            print('\n\n<<<<<<<<+>>>>>>>>')
            AdvanceAmount = GetDetails('Advance Amount', int, '10000')
            ReceiptNumber = GetDetails('Receipt Number', int, CanBeNONE=True)
            print('\n<<<<<<<<+>>>>>>>>\n')

            cursor.execute(f"UPDATE [Tenant's Information] SET [Advance Amount] = ?, [Receipt Number] = ?, [Current Status] = 'OCCUPIED' WHERE ID = '{TenantID}';", (AdvanceAmount, ReceiptNumber))
            cursor.commit()
            break
        elif ANS == 'FIND TENANT ID':
            print('\n>> Follow Along To Check For Tenant Details <<')
            FetchData_TenantID_FROM_TenantName(False)
        else:
            print('>> INVALID Response, TRY AGAIN <<')

def CustomAction_TenantVacatingAction():
    Update_ToDate_Field()
    Update_CurrentStatus_Field()

def CustomAction_ChangeOccupancyAction():
    VacatingTenant_List, Date = Update_ToDate_Field()
    for TenantID in VacatingTenant_List:
        InsertData_OccupancyInformation(TenantID, Date, 1)

# OTHER FUNCTIONS
RawData = None
def GetDetails(WhatToGet: str, DataType = str, DefaultValue = '', CanBeNONE = False, PossibleValues = [], StringType = None):
    def GetInput():
        global RawData
        RawData = input(f'\nEnter The {WhatToGet}: ').strip().upper()
    def InsertValue():
        gui.typewrite(DefaultValue)

    while True:
        GetInput_Thread = threading.Thread(target=GetInput)
        InsertValue_Thread = threading.Thread(target=InsertValue)
        GetInput_Thread.start()
        InsertValue_Thread.start()
        GetInput_Thread.join()
        if RawData != '':
            try:
                ConvertedData = DataType(RawData)
                if StringType == 'UPPER':
                    ConvertedData = ConvertedData.upper()
                elif StringType == 'CAPITALIZE':
                    ConvertedData = ' '.join([Word.capitalize() if Word.replace(',', '').isalpha() and not Word.isupper() else Word for Word in ConvertedData.split()])

                if not PossibleValues or ConvertedData in PossibleValues: 
                    return ConvertedData
                else:
                    print(f'INVALID {WhatToGet}, TRY AGAIN...')
            except ValueError:
                print(f'INVALID {WhatToGet}, TRY AGAIN...')
        elif CanBeNONE is None:
            print(f'INVALID {WhatToGet}, TRY AGAIN...')
        elif CanBeNONE:
            return None
        else:
            return 'NONE' if DataType == str else None

def Delete_DUEDetails():
    Today = datetime.date.today()
    Month = calendar.month_name[Today.month-2].upper()
    cursor.execute(f"DELETE FROM [DUE Details] WHERE [DUE Amount] = 0 AND [For The Month Of] = '{Month}';")

