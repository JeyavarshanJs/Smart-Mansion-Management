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
    ID, Date, VacatingTenant_List = InsertData_UnusualDepartureDetails()

    Month, ReceiptNumber_List = InsertData_PaymentDetailsNS(ID, VacatingTenant_List)

    for TenantID in VacatingTenant_List:
        cursor.execute(f"UPDATE [Occupancy Information] SET [To (Date)] = ? WHERE [Tenant ID] = '{TenantID}' AND [To (Date)] IS NULL;", (Date,))
        cursor.commit()

    Update_CurrentStatus_Field()

    if ID in Room_IDs:
        GenerateRoomRentReceipt_SPECIFIC(Month, ReceiptNumber_List)
    elif ID in Shop_IDs:
        GenerateShopRentReceipt_SPECIFIC(Month, ReceiptNumber_List)

