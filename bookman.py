## BOOKMAN
## by UltraChip
##
## Automatically reads books from Jonathan Basile's online implementation of Jorge Luis Borge's
## classic short story "The Library of Babel" (http://libraryofbabel.info). Bookman chooses a hex
## at random and then scans through all the books contained within, looking for evidence of actual,
## readable English language. 


# IMPORTS AND CONSTANTS
import random
import string
import sqlite3
import os
import time
import ollama
import re
import logging
import logging.config
import multiprocessing as mp
from math import ceil

import pybel
from configManager import loadConfig

confFile = "./bookman.conf"


# FUNCTIONS
def scanHex(wid):
    # Select a hex address at random and iterate over each book in that hex, scanning each one for
    # evidence of language.
    db = sqlite3.connect(conf['dbfile'])
    db.execute("PRAGMA isolation_level = SERIALIZABLE")

    dictionary = readDictionary(conf['dictfile'])

    while True:
        hex = buildAddr()
        logging.info(f"READER #{wid} - Scanning hex #{shorthex(hex)}")
        for wall in range(1, 4):
            for shelf in range(1, 5):
                for volume in range(1, 32):
                    book = pybel.browse(hex, str(wall), str(shelf), str(volume)).replace("\n", "")
                    #book = testbook()  # NOTE: Only uncomment this line when testing!
                    logging.info(f"READER #{wid} - Book downloaded. Reading...")
                    analyze(book, hex, str(wall), str(shelf), str(volume), db, dictionary, wid)
    db.close()
    return

def buildAddr():
    # Builds a randomized hex address
    chars = []
    alphabet = string.ascii_lowercase + string.digits
    length = random.randint(1, 3200)
    for c in range(length):
        chars.append(random.choice(alphabet))
    return ''.join(chars)

def analyze(book, hex, wall, shelf, volume, db, dictionary, wid):
    # Analyze the content of a book in conf['seglength'] sized chunks. First counts the number of
    # consecutive English words in a given segment and, if it surpasses the minimum wordcount,
    # hands the segment off to an LLM for final verification.
    i    = 1
    page = 1
    cursor = db.cursor()
    startTime = time.time()
    while i < (len(book)-conf['seglength']):
        segment = book[i:(i+conf['seglength'])]

        if (page*3200) < i:
            page = ceil(i/3200)
        
        wc = wCount(segment, dictionary)
        if wc >= conf['wordCount']:
            tstamp = time.strftime("%Y%m%d-%H%M%S",time.gmtime())
            llm = llmCheck(segment)
            cursor.execute("""INSERT INTO passages (tstamp, hex, wall, shelf, volume, page,
                            content, nScore, llm) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);""", 
                            (tstamp, hex, wall, shelf, volume, page, segment, wc, llm))
            db.commit()
            i += conf['seglength']
            if llm == 0:
                a=0
                #logging.info(f"FOUND - Segment passed word count check but NO LLM confirmation")
                #logging.info(f"{shorthex(hex)}-{wall}-{shelf}-{volume}, page {page}:")
                #logging.info(segment)
            else:
                logging.info(f"FOUND - Segment passed ALL checks!!!")
                logging.info(f"{shorthex(hex)}-{wall}-{shelf}-{volume}, page {page}:")
                logging.info(segment)
        else:
            i += 1

    readTime = (time.time()-startTime)/60  # Calculates reading time in minutes
    cursor.execute("SELECT books, readSpeed FROM stats WHERE sid = 1;")
    result = cursor.fetchone()
    booksRead = int(result[0])
    oldTotalMinutes = booksRead * result[1]
    booksRead += 1
    avgReadSpeed = (oldTotalMinutes+readTime) / booksRead
    cursor.execute("UPDATE stats SET books = ?, readSpeed = ? WHERE sid = 1", (booksRead, avgReadSpeed))
    db.commit()
    return

def wCount(segment, dictionary):
    # Identifies the longest chain of consecutive English words within the given segment, and
    # returns it as a numerical score.
    score    = 0
    curCount = 0
    splitSeg = re.split(r'\s*,\s*|\s*\.\s*|\s+', segment)

    for word in splitSeg:
        if word.strip() in dictionary:
            curCount += 1
            if curCount > score:
                score = curCount
        else:
            curCount = 0
    return score

def llmCheck(segment):
    # If a given segment is shown to have a high chance of containing language, then we pass it to
    # an Ollama server and ask it to perform a final confirmation. Returns 1 if the LLM believes
    # there is language, otherwise returns 0. 
    while True:
        thePrompt = f"{conf['llmPrompt']}\n\nThe test string is:\n{segment}"
        client = ollama.Client(host=conf['llmHost'])
        answer = client.generate(model=conf['llmModel'], prompt=thePrompt)
        yesno = answer['response'].strip()
        if yesno == '1':
            return 1
        elif yesno == '0':
            return 0

def shorthex(hex):
    # Shortens the hex address to the first 10 characters + last 10 characters to make things more
    # readable in logs and such.
    if len(hex) <= 20:
        return hex
    firstC = hex[:10]
    lastC  = hex[-10:]
    return f"{firstC}...{lastC}"

def initDB(filename):
    # Initializes the sqlite database which keeps track of found passages
    if not os.path.exists(filename):
        db = sqlite3.connect(filename)
        cursor = db.cursor()
        tab_passage = """CREATE TABLE passages (
                         pid INTEGER PRIMARY KEY,
                         tstamp TEXT,
                         hex TEXT,
                         wall TEXT,
                         shelf TEXT,
                         volume TEXT,
                         page INTEGER,
                         content TEXT,
                         nScore INTEGER,
                         llm INTEGER); """
        tab_stats = """CREATE TABLE stats (
                       sid INTEGER PRIMARY KEY,
                       books INTEGER,
                       readSpeed REAL);"""
        cursor.execute(tab_passage)
        cursor.execute(tab_stats)
        cursor.execute("INSERT INTO stats (books, readSpeed) VALUES (0, 0);")
        cursor.close()
        db.commit()
        db.close()
    return

def readDictionary(filename):
    # Reads in the dictionary file and returns it as a list.
    dictionary = {'a', 'is'}  # Pretty much the only low-character words we want in the list.
    with open(filename, 'r') as file:
        for line in file:
            word = line.strip()
            if len(word) > 2:  # We want to filter out smaller "words" in the list like dd and tr.
                word = word.lower()
                dictionary.add(word.strip())
    return dictionary

def testbook():
    # NOTE: THIS FUNCTION IS USED ONLY WHEN TESTING
    # Loads up the contents of a locally-stored test book (instead of downloading real books from
    # the Library) with five known-valid English sentences that you can use to test and tune the 
    # detection algorithms. 
    with open(conf['testfile'], 'r') as file:
        book = file.read()
    return book.replace("\n", "")


# INITIALIZATION
conf = loadConfig(confFile)

logging.config.dictConfig({    # This block silences log spam from imported modules so that only
    'version': 1,              # my own log messages get recorded.
    'disable_existing_loggers': True,
})
logging.basicConfig(
    level=conf['loglevel'],
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(conf['logfile'], mode='a'),
        logging.StreamHandler()])
logging.info("INIT - Logger")

initDB(conf['dbfile'])

workers = []
cCount = os.cpu_count() if conf['cCount'] == 0 else conf['cCount']
mp.get_context("spawn")
for w in range(cCount):
    worker = mp.Process(target=scanHex, args=(w,))
    workers.append(worker)
    worker.start()
    logging.info(f"INIT - Kicked off reader #{w}")

logging.info("INIT - All readers online, initialization complete")
while True:
    time.sleep(1)  # Just have the main thread idle while the worker threads do their thing.
