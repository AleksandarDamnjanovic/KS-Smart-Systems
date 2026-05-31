'''
*************** Name: KS Node
*************** Part of: KS Smart Systems
*************** Author: Aleksandar Damnjanovic AKA Kind Spirit
*************** YouTube channel: Kind Spirit Technology
*************** Date: 25.05.2026.
*************** Location: Kragujevac, Serbia
*************** Description:
                    Holds function that logs messages and errors in log file, defined in support.py.
'''

import support
from datetime import datetime
import os

def logit(text, type= 0):

    if not os.path.exists(support.logFile):
        with open(support.logFile, "w") as f:
            f.write("")

    if(type==0):
        type = "MESSAGE"
    elif (type==1):
        type = "ERROR"
    else:
        type = "WARNING"

    present = datetime.now()
    toPrint = present.strftime("%d.%m.%Y %H:%M:%S")
    message = f"\n*** {toPrint} *** {type}: {text}"

    with open(support.logFile, "r") as f:
        lines = f.readlines()
        if len(lines) > 2000:
            lines = lines[1000:]
            with open(support.logFile, "w") as f:
                f.writelines(lines)

    f= open(support.logFile, "a")
    f.write(message)
    f.close()
    print(message)