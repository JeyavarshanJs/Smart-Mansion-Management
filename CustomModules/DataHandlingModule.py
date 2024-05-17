def ReadPermanentData(Delimiter = ':'):
    with open('Data.txt', 'r') as File:
        for Line in File:
            Item = Line.strip().split(Delimiter, 1)
            Key, Value = Item
            Key = Key.strip()
            try:
                Value = eval(Value.strip())
            except Exception:
                Value = Value.strip()
            PermanentData[Key] = Value

def UpdatePermanentData(WhatToUpdate: list, Values: dict, Delimiter = ':'):
    for Element in WhatToUpdate:
        if Values.get(Element) is None:
            while True:
                Value = input(f'\nEnter {WhatToUpdate}: ')
                if isinstance(Value, type(PermanentData[Element])):
                    PermanentData[Element] = Value
                    break
                else:
                    print('>> INVALID Value, TRY AGAIN...')
        else:
            PermanentData[Element] = Values[Element]

    with open('Data.txt', 'w') as File:
        File.writelines([f'{Key}{Delimiter} {Value}\n' for Key, Value in PermanentData.items()])

    ReadPermanentData()


PermanentData = {}
ReadPermanentData()