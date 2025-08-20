## BOOK REPORT
## by UltraChip
##
## A companion utility to BookMan. Provides a way to easily browse and manage Bookman's findings.


# IMPORTS AND CONSTANTS
import sqlite3
import logging
import time
import math
from prettytable import PrettyTable as pt
from shutil import get_terminal_size

from configManager import loadConfig

confFile = "./bookman.conf"


# FUNCTIONS

def main(viewMode):
    # Main menu function
    stats, passages, loadtime = loadDB(conf['dbfile'])
    vString = "LLM Only" if viewMode == 1 else "All Entries"

    clearScreen()
    print(colSpacer(["BOOKMAN REPORTING UTILITY"], "="))
    line = [f"View Mode: {vString}",
            f"DB Loaded On: {time.strftime("%d %b %Y at %H:%M%S", time.localtime(loadtime))}"]
    print(colSpacer(line))
    line = [f"Books Read: {stats[0]:,}",
            f"Avg Speed: {stats[1]:.2f} seconds per book"]
    print(colSpacer(line))
    print(f"{div()}\n")
    tHeaders = ["Index", "Time Found", "Address", "Page", "Content", "Score"]
    if viewMode == 0:
        tHeaders.append("LLM")
    table = pt(tHeaders)
    for p in passages:
        tEntry = [p[0], p[1], p[2], p[3], p[4], p[5]]
        if viewMode == 1:
            tEntry.append(p[6])
        table.add_row(tEntry)
    print(table)
    print(f"{div()}\n")
    
    return

def clearScreen():
    # Self explanatory
    print("\033c")

def div(pad="="):
    return pad*swidth+"\n"

def colSpacer(options, pad=" "):
    # Evenly spaces strings along the column width of the screen. Useful for
    # cleanly printing menu options.
    fString = ""
    num_options = len(options)
    if num_options == 1:
        return options[0]
    spacePerCol = int(math.floor((swidth - len(options[-1])) / (num_options - 1)))
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
    return stats, passages, time.time()

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
conf     = loadConfig(confFile)
swidth   = getWidth()
viewMode = conf['viewmode']

logging.basicConfig(
    level=conf['loglevel'],
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(conf['reportlog'], mode='a')])

main(viewMode)