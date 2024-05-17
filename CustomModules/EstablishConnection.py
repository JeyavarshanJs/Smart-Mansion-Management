import pyodbc

from CustomModules.DataHandlingModule import *

# Establish Connection
try:
    con = pyodbc.connect(r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + rf'{PermanentData['Database Path']};')
    cursor = con.cursor()
except Exception:
    print('Database Connection FAILED') 

