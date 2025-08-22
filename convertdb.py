## BOOKMAN DATABASE CONVERTER
##
## Simple converter 

import sqlite3
from datetime import datetime
from configManager import loadConfig

conf = loadConfig("./bookman.conf")

db = sqlite3.connect(conf['dbfile'])
cursor = db.cursor()
cursor.execute("SELECT pid, tstamp FROM passages;")
table = cursor.fetchall()
for row in table:
    pid    = row[0]
    tstamp = row[1]
    newtstamp = datetime.strptime(tstamp, '%Y%m%d-%H%M%S').timestamp()
    cursor.execute("UPDATE passages SET tstamp = ? WHERE pid = ?", (newtstamp, pid))
cursor.close()
db.commit()
db.close()

print(f"Converted {len(table)} records.")