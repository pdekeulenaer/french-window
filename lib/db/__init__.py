# imports
from sqlite_db import SQLiteConn

_DBNAME = 'data/french_window.db'
_DBNAME_TEST = 'data/test_french_window.db'
_DB_TYPE = 'sqlite'

if 'DBNAME' not in locals():
    DBNAME = _DBNAME

if 'DBNAME_TEST' not in locals():
    DBNAME_TEST = _DBNAME_TEST

if 'DB_TYPE' not in locals():
    DB_TYPE = _DB_TYPE


def get_db():
    if DB_TYPE == 'sqlite':
        db = SQLiteConn(DBNAME)
        return db
    else:
        print 'DATABASE HANDLER NOT AVAILABLE'
        return None
