import sqlite3
import sqlite_db

class Connection(object):
    def __init__(self, db):
        self.db = db
        self.conn = sqlite3.connect(db)
        self.c = self.conn.cursor()

    def execute(self, qobj):
        sql = qobj.createSQL()
        self.db_execute(sql)
        if qobj.STORE_RESULTS:
            return self.fetch(qobj.fields)
        return None

    def db_execute(self, sql):
        self.c.execute(sql)
        self.conn.commit()

    def fetch(self, fields):
        res = self.c.fetchall()
        res = map(lambda l: dict(zip(fields, l)), res)
        return res

class QueryObject(object):
    STORE_RESULTS = False

    def __init__(self, schema):
        self.schema = schema
        (self.table, self.fields) = schema.full_view()
        self.where = []
        self.sort = []
        self.limit = None

    def createSQL(self):
        print "ERR - to be implemented"

    def filterSQL(self):
        if len(self.where) == 0:
            return ''
        return 'WHERE %s' % (' AND '.join(self.where))

    def sortSQL(self):
        if len(self.sort) == 0:
            return ''
        return 'ORDER BY %s' % (', '.join(self.sort))

    def add_filter(self, field, value, exact=True):
        if not(exact):
            value = "%%%s%%" % (value)
        if exact:
            operator = '='
        else:
            operator = 'LIKE'
        self.where.append("%s %s '%s'" % (field, operator, value))

    def add_sort(self, field, asc=True):
        if asc:
            operator = 'ASC'
        else:
            operator = 'DESC'
        self.sort.append("%s %s" % (field, operator))


class Select(QueryObject):

    STORE_RESULTS = True

    def createSQL(self):
        fieldlist = ', '.join(self.fields)
        sql = 'SELECT %s FROM %s %s %s' % (fieldlist, self.table, self.filterSQL(), self.sortSQL())
        print sql
        return sql

if __name__ == '__main__':
    db = Connection('db/french_window.db')
    qobj = Select()


    fields = ('id','title','author_id', 'summary', 'publisher', 'is_series', 'series_nr', 'isbn13', 'isbn10', 'language')

