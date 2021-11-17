# log_print.py
from datetime import datetime


# Log Print
async def log_print(text):
    print('[' + datetime.now().strftime("%x %X") + '] ' + text)
    with open('log.txt', 'a') as log_file:
        log_file.write('[' + datetime.now().strftime("%x %X") + '] ' + text + "\n")
