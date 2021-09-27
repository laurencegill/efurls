import sqlite3
import secrets

with open('config.py', 'w') as f:
    print('SECRET_KEY = ' '\'' + secrets.token_urlsafe(32) + '\'', file=f)

connection = sqlite3.connect('efurls.db')

with open('efschema.sql') as f:
    connection.executescript(f.read())

connection.commit()
connection.close()
