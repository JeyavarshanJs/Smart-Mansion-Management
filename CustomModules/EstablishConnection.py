import pyodbc

# Establish Connection
try:
    con = pyodbc.connect(r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=D:\Python Projects\Smart-Mansion-Management\Database (MS Access).accdb;')
except:
    print('Database Connection FAILED') 

# Create a Cursor
cursor = con.cursor()
