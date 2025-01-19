import sqlite3
import os
#if os.path.exists("GBN.db"):
  #os.remove("GBN.db")
with open('db.sql', 'r') as sql_file:
    sql_script = sql_file.read()

db = sqlite3.connect('GBN.db')
cursor = db.cursor()
cursor.executescript(sql_script)
db.commit()
db.close()
