import sys, time
import win32print, win32con

def GETPrinters():
    # SELECTING A PRINTER
    AvailablePrinters = [Printer[2] for Printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)]
    ActivePrinters = []
    for Printer in AvailablePrinters:
        PrinterOBJ = win32print.OpenPrinter(Printer)
        PrinterINFO = win32print.GetPrinter(PrinterOBJ, 2)
        if PrinterINFO['Status'] == 0:
            ActivePrinters.append(Printer)

    if len(ActivePrinters) != 0:
        return (ActivePrinters, True)

def ChoosePrinter(ActivePrinters: list):
    global ChosenPrinter
    if len(ActivePrinters) > 1:
        print('\nAVAILABLE PRINTERS:')
        for i, Choice in enumerate(ActivePrinters):
            print(f'{i+1})', Choice)

        while True:
            User_Choice = input('\nEnter Your Choice ID: ')
            if User_Choice == '' and 'EPSON1A2AB1 (M100 Series)' in ActivePrinters:
                User_Choice = ActivePrinters.index('EPSON1A2AB1 (M100 Series)')
                break
            elif User_Choice in [str(i+1) for i in range(len(ActivePrinters))]:
                User_Choice = int(User_Choice) - 1
                break
            else:
                print('>>> ID Not Defined, TRY AGAIN... <<<')
        print('<<<<<<<<<<+>>>>>>>>>>')

        ChosenPrinter = ActivePrinters[User_Choice]

    elif len(ActivePrinters) == 1:
        if ActivePrinters[0] == 'EPSON1A2AB1 (M100 Series)':
            ChosenPrinter = ActivePrinters[0]
        else:
            print(f">>> Do You Want To Proceed Printing With Printer '{ActivePrinters[0]}'? (Y/N) <<<").strip().upper()
            User_Choice = input('Enter Your Choice: ')

            if User_Choice == 'Y':
                ChosenPrinter = ActivePrinters[0]
            elif User_Choice == 'N':
                print('\n', '-' * 50, sep='')
                print("No Printer SELECTED, Printing SKIPPED...")
                print('-' * 50, '\n', sep='')

def Print(ReceiptNumber_List, PaperWidth, PaperLength, FileType):
    print('\n>>> Printing In PROGRESS <<<')
    for ReceiptNumber in ReceiptNumber_List:
        try:
            FileOBJ = open()
            Data = FileOBJ.read()
            FileOBJ.close()

            PrinterOBJ = win32print.OpenPrinter(ChosenPrinter)
            PrinterINFO = win32print.GetPrinter(PrinterOBJ, 2)

            PrinterProperties = PrinterINFO["pDevMode"]
            PrinterProperties.PaperSize = win32con.DMPAPER_USER         # Custom paper size
            PrinterProperties.PaperWidth = PaperWidth
            PrinterProperties.PaperLength = PaperLength
            PrinterProperties.Orientation = win32con.DMORIENT_PORTRAIT  # Portrait orientation
            PrinterProperties.PrintQuality = 0                          # Draft quality (0 = Draft; 1 = Normal; 2 = High)
            PrinterProperties.Scale = 100                               # 100% Size (No Scaling)
            PrinterProperties.Copies = 1                                # Number of copies

            win32print.StartDocPrinter(PrinterOBJ, 1, ("Mansion Rent Receipt", None, "RAW"))
            win32print.StartPagePrinter(PrinterOBJ)
            win32print.WritePrinter(PrinterOBJ, Data)
            win32print.EndPagePrinter(PrinterOBJ)
            win32print.EndDocPrinter(PrinterOBJ)

            print('\n>>> Printing In PROGRESS... <<<\n')
            time.sleep(10)

            win32print.ClosePrinter(PrinterOBJ)
        except Exception as E:
            print('\n', '-' * 80, sep='')
            print(f"Error ENCOUNTERED While Printing, ({E})")
            print('-' * 80, '\n', sep='')
            sys.exit()
