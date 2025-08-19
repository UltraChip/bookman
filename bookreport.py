## BOOK REPORT
## by UltraChip
##
## A companion utility to BookMan. Provides a way to easily browse and manage Bookman's findings.


# IMPORTS AND CONSTANTS
import sqlite3
import logging
from prettytable import PrettyTable as pt

from configManager import loadConfig

confFile = "./bookman.conf"


# FUNCTIONS

def main():
    # Main menu function
    stats, passages = loadDB(conf['dbfile'])
    return

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


# INITIALIZATION
conf = loadConfig(confFile)

logging.basicConfig(
    level=conf['loglevel'],
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(conf['reportlog'], mode='a')])

main()