from CustomModules.EstablishConnection import *
from CustomModules.VariablesModule import *
from CustomModules.UpdateModule import *
from CustomModules.GenerateRentReceiptModule import *
from CustomModules.InsertDataModule import *
from CustomModules.DuplicateRecordsModule import *

def CustomAction_MonthEndAction():
    DuplicateRecords_MonthlyReportData()
    Update_ClosingReading_Field()

    input('\nPress ENTER Key To Continue...')
    Update_NumberOfDaysOccupied_Field()

def CustomAction_MonthBeginningAction():
    Update_TenantsCount_Field()
    
    print("\n\n>>>Follow Along To Update 'Total Rent' Field <<<")
    Update_TotalRent_Field()
    
    print("\n\n>>>Follow Along To Update 'Individual Rent' Field <<<")
    Update_IndividualRent_Field()
    
    DuplicateRecords_DUEDetails()
    DuplicateRecords_PaymentDetails()

def CustomAction_UnusualDepartureAction():
    ID, Date = InsertData_UnusualDepartureDetails()

    Month, ReceiptNumber_List = InsertData_PaymentDetailsNS(ID)

    cursor.execute(f"UPDATE [Occupancy Information] SET [To (Date)] = ? WHERE [Room/Shop ID] = '{ID}' AND [To (Date)] IS NULL;", (Date,))
    cursor.commit()

    if ID in Room_IDs:
        GenerateRoomRentReceipt_SPECIFIC(Month, ReceiptNumber_List)
    elif ID in Shop_IDs:
        GenerateShopRentReceipt_SPECIFIC(Month, ReceiptNumber_List)

