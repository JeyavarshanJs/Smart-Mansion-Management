import pyodbc
import os, sys, time

from CustomModules.DataHandlingModule import *


if PermanentData['Database Path'] == '':
    UpdatePermanentData(['Database Path'], {'Database Path': rf'{os.getcwd()}\Database (MS Access).accdb'})

# Establish Connection
try:
    con = pyodbc.connect(r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + rf'{PermanentData['Database Path']};')
    cursor = con.cursor()
except Exception:
    print('>> Database Connection FAILED <<') 
    time.sleep(3)
    sys.exit()  

