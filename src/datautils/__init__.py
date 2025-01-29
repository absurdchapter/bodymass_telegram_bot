import os
import sqlite3

sqlite_db_path = 'data/bodymass.sqlite'
sql_header_path = 'data/bodymass.sql'

if not os.path.exists(sqlite_db_path) or os.environ.get('UPDATE_DATABASE'):
    with sqlite3.connect(sqlite_db_path) as db_:
        with open(sql_header_path, 'r') as sql_header:
            for command in sql_header.read().split(';'):
                db_.execute(command)
