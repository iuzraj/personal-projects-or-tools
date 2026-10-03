import config
import sqlite3


con = sqlite3.connect(config.DATABASE_FILE)
cur = con.cursor()


with open(config.SCHEMA_FILE) as f:
    script = f.read()
    cur.executescript(script)
    
    
cur.close()
con.close()