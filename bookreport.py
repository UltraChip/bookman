## BOOK REPORT
## by UltraChip
##
## A companion utility to BookMan. Provides a way to easily browse and manage Bookman's findings.


# IMPORTS AND CONSTANTS
import sqlite3
import time
import math
from prettytable import PrettyTable as pt
from shutil import get_terminal_size

from configManager import loadConfig

confFile = "./bookman.conf"


# FUNCTIONS
def main(viewMode, tz):
    # Main menu function
    stats, passages, loadtime = loadDB()
    while True:
        choice = "NOCHOICE"
        vString = "LLM Only" if viewMode == 1 else "All Entries"
        tString = "UTC" if tz == 'utc' else "Local"

        clearScreen()
        print(colSpacer(["","BOOKMAN REPORTING UTILITY",""], "="))
        line = [f"Books Read: {stats[0]:,}",
                f"DB Loaded On: {time.strftime('%d %b %Y at %H:%M:%S', time.localtime(loadtime))}"]
        print(colSpacer(line))
        line = [f"Avg Speed:  {stats[1]:.2f} seconds per book",
                f"View Mode:  {vString}"]
        print(colSpacer(line))
        print(f"Time Zone:  {tString}")
        print(f"{div()}")
        tHeaders = ["Index", "Time Found", "Address", "Page", "Content", "Score"]
        if viewMode == 0:
            tHeaders.append("LLM")
        table = pt(tHeaders)
        for p in passages:
            if tz == "utc":
                tstamp = time.strftime("%d %b %Y at %H:%M:%S", time.gmtime(float(p[1])))
            else:
                tstamp = time.strftime("%d %b %Y at %H:%M:%S", time.localtime(float(p[1])))
            tEntry = [p[0], tstamp, p[2], p[3], p[4], p[5]]
            if viewMode == 0:
                tEntry.append(p[6])
                table.add_row(tEntry)
            else:
                if p[6] == 1:
                    table.add_row(tEntry)
        print(table)
        print(f"{div()}\n")
        line = ["M - Toggle View Mode",
                "D - Delete Entry",
                "T - Change Timezone",
                "R - Refresh",
                "Q - Quit"]
        print("Enter index # to view get URL or...")
        print(colSpacer(line))

        choice = input("\nYour selection: ")
        if choice.upper() == "M":
            viewMode = 1 if viewMode == 0 else 0
        elif choice.upper() == "D":
            deleteEntry()
        elif choice.upper() == "T":
            tz = 'utc' if tz == 'local' else 'local'
        elif choice.upper() == "R":
            stats, passages, loadtime = loadDB()
        elif choice.upper() == "Q":
            return
        else:
            try:
                nchoice = int(choice)
            except:
                pass
            getURL(nchoice)

def getURL(pid):
    # Gives you a browsable link to a given Library of Babel book.
    db = sqlite3.connect(conf['dbfile'])
    cursor = db.cursor()
    cursor.execute("SELECT hex, wall, shelf, volume, page FROM passages WHERE pid == ?;", (pid,))
    result = cursor.fetchone()
    db.close()

    qString = f"{result[0]}-w{result[1]}-s{result[2]}-v{result[3]}:{result[4]}"
    link = f"https://libraryofbabel.info/book.cgi?{qString}"

    print(link)
    a = input("\n\nPress Enter to go back to main menu")
    return

def deleteEntry():
    # Deletes an entry from the database.
    try:
        choice = int(input("\nEnter the index number you want to delete: "))
    except:
        print("Invalid number!")
        time.sleep(3)
        return
    yesno = input(f"\nOk, we're about to delete entry #{choice}, are you ABSOLUTELY sure (y/N)?").upper()
    if yesno == "Y" or yesno == "YES":
        db = sqlite3.connect(conf['dbfile'])
        cursor = db.cursor()
        cursor.execute("DELETE FROM passages WHERE pid==?;", (choice,))
        db.commit()
        db.close()
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

def loadDB():
    # Loads in the contents of the database.
    passages = []
    db = sqlite3.connect(conf['dbfile'])
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

main(conf['viewmode'], conf['tz'])
