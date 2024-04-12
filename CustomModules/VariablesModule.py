# Global Static Variables
MonthNames = {'JAN': 'JANUARY', 'FEB': 'FEBRUARY', 'MAR': 'MARCH', 'APR': 'APRIL', 'MAY': 'MAY', 'JUN': 'JUNE', 'JUL': 'JULY', \
              'AUG': 'AUGUST', 'SEP': 'SEPTEMBER', 'OCT': 'OCTOBER', 'NOV': 'NOVEMBER', 'DEC': 'DECEMBER'}
Room_IDs = ['202', '203', '204', '205', '206', '207', '208', '301', '302', '303', '304', '305', '306', '307', '308', 'S2', 'S3']
Shop_IDs = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'A1', 'A2', 'A3', 'S1', 'MILL', '101', '102', '103', '104', '105', '106', '107', '108', '201']

# Global Dynamic Variables
ChosenDrive = ''
ChosenPrinter = None

# MENU AND SUB_MENU
MAIN_MENU = ['EXIT', 'UPDATE', 'GENERATE RENT RECEIPT', 'CHECK FOR CONSISTENCY', 'DUPLICATE RECORDS', 'FETCH DATA', 'INSERT DATA', 'CUSTOM ACTION']

SUB_MENU_UPDATE = ['BACK', 'Tenant Name', 'Total Rent', 'Individual Rent', 'Tenant Count', 'Current Status', 'Closing Sub-Meter Reading', 'Number Of Days Occupied']
SUB_MENU_UPDATE_TenantName = ['BACK', 'Occupancy Information', 'Payment Details']

SUB_MENU_GENERATE_RENT_RECEIPT = ['BACK', 'ROOM', 'SHOP']
SUB_MENU_GENERATE_RENT_RECEIPT_ROOM = ['BACK', 'ALL', 'SPECIFIC']
SUB_MENU_GENERATE_RENT_RECEIPT_SHOP = ['BACK', 'ALL', 'SPECIFIC']

SUB_MENU_CHECK_FOR_CONSISTENCY = ['BACK', 'Receipt Number', 'Room_ID AND Shop_ID']

SUB_MENU_DUPLICATE_RECORDS = ['BACK', 'Monthly Report Data', 'DUE Details', 'Payment Details']

SUB_MENU_FETCH_DATA = ['BACK', 'Tenant_ID --> Tenant_Name', 'Tenant_Name --> Tenant_ID', 'Room/Shop_ID --> TenantID', 'TenantID --> Receipt Number', \
                       'UNPAID Tenants', 'Get Tenant Details', 'Vacant Room/Shop', 'Total Cash Received', 'Units Consumed']

SUB_MENU_INSERT_DATA = ['BACK', 'Water Purchase Details', 'Unusual Departure Details', 'Payment Details (NS)']

SUB_MENU_CUSTOM_ACTION = ['BACK', 'Month End Action', 'Month Beginning Action', 'Unusual Departure Action']
