## BOOK REPORT
## by UltraChip
##
## A companion utility to BookMan. Provides a way to easily browse and manage Bookman's findings.


# IMPORTS AND CONSTANTS
import sqlite3
import logging
from prettytable import PrettyTable as pt
from shutil import get_terminal_size

from configManager import loadConfig

confFile = "./bookman.conf"


# FUNCTIONS

def main():
    # Main menu function
    stats, passages = loadDB(conf['dbfile'])
    swidth = getWidth()

    clearScreen()
    print(colSpacer(["BOOKMAN REPORTING UTILITY"], swidth, "="))
    return

def clearScreen():
    # Self explanatory
    print("\033c")

def colSpacer(options, swidth, pad=" "):
    # Evenly spaces strings along the column width of the screen. Useful for
    # cleanly printing menu options.
    fString = ""
    num_options = len(options)
    if num_options == 1:
        return options[0]
    spacePerCol = int(floor((swidth - len(options[-1])) / (num_options - 1)))
    for i, option in enumerate(options):
        if i == len(options)-1:
            break
        spacer = pad*(spacePerCol-len(option))
        options[i] = option+spacer
    for option in options:
        fString = fString + option
    return fString

def shorthex(hex):
    # Shortens the hex address to the first 10 characters + last 10 characters to make things more
    # readable in logs and such.
    if len(hex) <= 20:
        return hex
    firstC = hex[:10]
    lastC  = hex[-10:]
    return f"{firstC}...{lastC}"

def loadDB(filename):
    # Loads in the contents of the database.
    passages = []
    db = sqlite3.connect(filename)
    cursor = db.cursor()
    cursor.execute("SELECT books, readSpeed FROM stats WHERE sid == 1;")
    stats = cursor.fetchone()
    cursor.execute("SELECT * from passages;")
    rawP = cursor.fetchall()
    for row in rawP:
        addr = buildAddr(row[2], row[3], row[4], row[5])
        passages.append([row[0], row[1], addr, row[6], row[7], row[8], row[9]])
    return stats, passages

def buildAddr(hex, wall, shelf, volume):
    # Concatenates the various elements of a Babel book address in to a single, readable string.
    sHex = shorthex(hex)
    addr = f"{sHex}-{wall}-{shelf}-{volume}"
    return addr

def getWidth():
    # Attempts to detect the width of the terminal (in characters). If auto-detect fails, defaults
    # to 100.
    try:
        return get_terminal_size().columns
    except:
        return 100


# INITIALIZATION
conf = loadConfig(confFile)

logging.basicConfig(
    level=conf['loglevel'],
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(conf['reportlog'], mode='a')])

main()