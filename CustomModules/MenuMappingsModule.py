from CustomModules.UpdateModule import *
from CustomModules.GenerateRentReceiptModule import *
from CustomModules.FetchDataModule import *
from CustomModules.DuplicateRecordsModule import *
from CustomModules.CheckConsistencyModule import *
from CustomModules.CustomActionModule import *
from CustomModules.InsertDataModule import *
from CustomModules.SendNotificationModule import *



# MAIN MENU
MAIN_MENU = [['EXIT', lambda: 'QUIT'], ['UPDATE'], ['GENERATE RENT RECEIPT'], ['CHECK CONSISTENCY'], ['DUPLICATE RECORDS'], ['FETCH DATA'], ['INSERT DATA'], ['SEND NOTIFICATION', lambda: SendNotification_ALL()], ['CUSTOM ACTION']]

# SUB MENU (UPDATE)
SUB_MENU_UPDATE = [['BACK', lambda: 'BACK'],
                   ['DUE Amount', lambda: Update_DUEAmount_Field()],
                   ['Total Rent', lambda: Update_TotalRent_Field()],
                   ['Individual Rent', lambda: Update_IndividualRent_Field],
                   ['Tenant Count', Update_TenantsCount_Field],
                   ['Current Status', Update_CurrentStatus_Field],
                   ['Closing Sub-Meter Reading', Update_ClosingReading_Field],
                   ['Number Of Days Occupied', Update_NumberOfDaysOccupied_Field]]

# SUB MENU (GENERATE RENT RECEIPT)
SUB_MENU_GENERATE_RENT_RECEIPT = [['BACK', lambda: 'BACK'], ['ROOM'], ['SHOP']]
SUB_MENU_GENERATE_RENT_RECEIPT_ROOM = [['BACK', lambda: 'BACK'],
                                       ['ALL', lambda: GenerateRoomRentReceipt_ALL()],
                                       ['SPECIFIC', lambda: GenerateRoomRentReceipt_SPECIFIC()],
                                       ['EXCEPT', lambda: GenerateRoomRentReceipt_EXPECT()]]
SUB_MENU_GENERATE_RENT_RECEIPT_SHOP = [['BACK', lambda: 'BACK'],
                                       ['ALL', lambda: GenerateShopRentReceipt_ALL()],
                                       ['SPECIFIC', lambda: GenerateShopRentReceipt_SPECIFIC()],
                                       ['EXCEPT', lambda: GenerateShopRentReceipt_EXPECT()]]

# SUB MENU (CHECK CONSISTENCY)
SUB_MENU_CHECK_CONSISTENCY = [['BACK', lambda: 'BACK'], ['Room_ID AND Shop_ID', lambda: CheckConsistency_ID()]]

# SUB MENU (DUPLICATE RECORDS)
SUB_MENU_DUPLICATE_RECORDS = [['BACK', lambda: 'BACK'], 
                              ['Monthly Report Data', lambda: DuplicateRecords_MonthlyReportData()],
                              ['DUE Details', lambda: DuplicateRecords_DUEDetails()],
                              ['Payment Details', lambda: DuplicateRecords_PaymentDetails()]]

# SUB MENU (FETCH DATA)
SUB_MENU_FETCH_DATA = [['BACK', lambda: 'BACK'],
                       ['Tenant_ID --> Tenant_Name', lambda: FetchData_TenantName_FROM_TenantID()], 
                       ['Tenant_Name --> Tenant_ID', lambda: FetchData_TenantID_FROM_TenantName()],
                       ['Room/Shop_ID --> TenantID', lambda: FetchData_TenantID_FROM_OccupiedSpaceID()], 
                       ['TenantID --> Receipt Number', lambda: FetchData_ReceiptNumber_FROM_TenantID()],
                       ['UNPAID Tenants', lambda: FetchData_UNPAID_Tenants()],
                       ['Get Tenant Details', lambda: FetchData_GetTenantDetails()],
                       ['Vacant Room/Shop', lambda: FetchDate_Vacancy()],
                       ['Total Cash Received', lambda: FetchData_TotalCashReceived()]]

# SUB MENU (INSERT DATA)
SUB_MENU_INSERT_DATA = [['BACK', lambda: 'BACK'],
                        ['Water Purchase Details', lambda: InsertData_WaterPurchaseDetails()],
                        ['Unusual Departure Details', lambda: InsertData_UnusualDepartureDetails()],
                        ['Payment Details (NS)', lambda: InsertData_PaymentDetailsNS()]]

# SUB MENU (CUSTOM ACTION)
SUB_MENU_CUSTOM_ACTION = [['BACK', lambda: 'BACK'],
                          ['Month End Action', lambda: CustomAction_MonthEndAction()],
                          ['Month Beginning Action', lambda: CustomAction_MonthBeginningAction()],
                          ['Unusual Departure Action', lambda: CustomAction_UnusualDepartureAction()],
                          ['New Occupancy Action', lambda: None]]


# CREATE MENU MAPPINGS
MENU_MAPPINGS = {}
def CreateMappings(MENUS, SUB_MENU_PREFIX, MENU_MAPPINGS):
    for ID, MENU in enumerate(MENUS):
        if f'{SUB_MENU_PREFIX}_{MENU[0].replace(' ', '_')}' in globals():
            SUB_MENU_MAPPINGS = {}
            CreateMappings(globals()[f'{SUB_MENU_PREFIX}_{MENU[0].replace(' ', '_')}'], f'{SUB_MENU_PREFIX}_{MENU[0].replace(' ', '_')}', SUB_MENU_MAPPINGS)
            MENU_MAPPINGS[str(ID + 1)] = [MENU[0], SUB_MENU_MAPPINGS]
        else:
            MENU_MAPPINGS[str(ID + 1)] = MENU

CreateMappings(MAIN_MENU, 'SUB_MENU', MENU_MAPPINGS)

# SET PUBLIC VARIABLES
__all__ = ['MENU_MAPPINGS']
