# SQLite database connection

import sqlite3

class Connection(object):
    pass

class SQLiteConn(Connection):
    def __init__(self, db):
        self.db = db
        self.conn = sqlite3.connect(db)
        self.c = self.conn.cursor()

    def execute(self, qobj):
        sql = qobj.createSQL()
        self.db_execute(sql)
        if qobj.STORE_RESULTS:
            return self.fetch(qobj.fields)

    def db_execute(self, sql):
        self.c.execute(sql)
        self.conn.commit()

    def fetch(self, fields):
        res = self.c.fetchall()
        res = map(lambda l: dict(zip(fields, l)), res)
        return res

    # Unit test written
    def store(self, schema, valuemap):
        fields = valuemap.keys()

        values = []
        for v in valuemap.values():
            if type(v) == int:
                values.append(str(v))
            else:
                values.append("'%s'" % (v))

        fstr = ', '.join(map(str,list(fields)))
        qstr = ', '.join(values)
        query = 'INSERT INTO %s (%s) VALUES (%s) ;' % (schema.table, fstr, qstr)

        # gets the row ID that was inserted
        self.c.execute(query)
        entryid = self.c.lastrowid
        self.conn.commit()

        return entryid

    # tested
    def update(self, schema, pk, valuemap):
        pairs = []
        for (f,v) in valuemap.items():
            if type(v) == int:
                pairs.append("%s = '%s'" % (f,v))
            else:
                pairs.append("%s = '%s'" % (f,v))

        vstr = ', '.join(pairs)

        if type(pk) == int:
            query = 'UPDATE %s SET %s WHERE %s = %s' % (schema.table, vstr, schema.primary_key, pk)
        else:
            query = "UPDATE %s SET %s WHERE %s = '%s'" % (schema.table, vstr, schema.primary_key, pk)

        self.c.execute(query)
        self.conn.commit()

    # tested
    def delete(self, schema, filtermap):
        fstr = []

        for (k,o,v) in filtermap:
            if type(v) == int:
                fstr.append('(%s %s %s)' % (k,o,v))
            else:
                fstr.append("(%s %s '%s')" % (k,o,v))

        filterq = 'AND '.join(fstr)
        query = 'DELETE FROM %s WHERE ( %s ) ;' % (schema.table, filterq)
        # execute

        self.c.execute(query)
        self.conn.commit()


    # TODO - merge with search
    def select(self, schema, valuemap, sort={}, singleRes=True):
        qobj = Select(schema)

        for (f,v) in valuemap.items():
            qobj.add_filter(f,v,True)
        for (f,o) in sort.items():
            qobj.add_sort(f, o)

        res = self.execute(qobj)

        if len(res) == 0:   return None
        if singleRes:       return res[0]

        return res

    def count(self, schema, valuemap):
        # get field list
        (table, _) = schema.full_view()

        f = []
        # get filter
        for (field, value) in valuemap.items():
            if type(value) == int:
                f.append('%s = %s' % (field, value))
            else:
                f.append("%s = '%s'" % (field, value))

        fullfilter = ' AND '.join(f)

        # build query
        if (len(fullfilter)>0):
            q = 'SELECT COUNT(*) FROM %s WHERE %s' % (table, fullfilter)
        else:
            q = 'SELECT COUNT(*) FROM %s' % (table)

        self.c.execute(q)
        self.conn.commit()

        res = self.c.fetchone()[0]
        return int(res)

    # select all objects satisfying the valuemap, return a dictionary per record
    # unit test written
    def select_all(self, schema, valuemap, sort={}):
        return self.select(schema, valuemap, singleRes=False)

    # tested
    def search(self, schema, exactmap={}, approxmap={}, sort={}):
        qobj = Select(schema)

        for (f,v) in exactmap.items():
            qobj.add_filter(f,v,True)
        for (f,v) in approxmap.items():
            qobj.add_filter(f,v,False)
        for (f,o) in sort.items():
            qobj.add_sort(f, o)

        res = self.execute(qobj)
        return res


    @staticmethod
    def connect(self):
        db = SQLiteConn()
        return db

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
        return sql

if __name__ == '__main__':
    db = SQLiteConn('db/french_window.db')
    fields = ('id','title','author_id', 'summary', 'publisher', 'is_series', 'series_nr', 'isbn13', 'isbn10', 'language')
    # db.select_all('books', fields, {})

    # db.update('books', 41, ('title','summary'),('john malkovich','is awesome'))
    # print len(db.select_all('books',fields,{'author_id':30}))

    # print db.search_all('books', fields, {'title':'eye'})
