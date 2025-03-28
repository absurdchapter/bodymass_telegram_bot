import dataclasses
import os
import sqlite3

sqlite_db_path = 'data/bodymass.sqlite'
sql_header_path = 'data/bodymass.sql'


def update_database_schema():
    with sqlite3.connect(sqlite_db_path) as db_:
        with open(sql_header_path, 'r') as sql_header:
            for command in sql_header.read().split(';'):
                db_.execute(command)


if not os.path.exists(sqlite_db_path):
    update_database_schema()

date_format = "%Y/%m/%d"


def dataclass_field_names(cls: type):
    assert hasattr(cls, '__dataclass_fields__')
    return [field.name for field in dataclasses.fields(cls)]
