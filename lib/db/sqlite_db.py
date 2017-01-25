# SQLite database connection

import sqlite3

class Connection(object):
    pass

class SQLiteConn(Connection):
    def __init__(self, db):
        self.db = db
        self.conn = sqlite3.connect(db)
        self.c = self.conn.cursor()


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

    # Returns a dictionary with key -> value
    # Unit test written
    def select(self, schema, valuemap, singleRes=True):
        # get field list
        (table, fields) = schema.full_view()
        fieldlist = ', '.join(fields)

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
            q = 'SELECT %s FROM %s WHERE %s' % (fieldlist, table, fullfilter)
        else:
            q = 'SELECT %s FROM %s' % (fieldlist, table)

        self.c.execute(q)
        self.conn.commit()

        if singleRes:
            res = self.c.fetchone()
            if res is None:
                return None
            return dict(zip(fields, res))
        else:
            res = self.c.fetchall()
            res = map(lambda l: dict(zip(fields, l)),res)
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
    def select_all(self, schema, valuemap):
        return self.select(schema, valuemap, singleRes=False)

    # tested
    def search(self, schema, exactmap={}, approxmap={}):
        # get field list
        (table, fields) = schema.full_view()
        fieldlist = ', '.join(fields)

        f = []
        # get filter
        for (field, value) in approxmap.items():
            f.append("%s LIKE '%%%s%%'" % (field, value))
        for (field, value) in exactmap.items():
            f.append("%s = '%s'" % (field, value))

        fullfilter = ' AND '.join(f)

        # build query
        if (len(fullfilter)>0):
            q = 'SELECT %s FROM %s WHERE %s' % (fieldlist, table, fullfilter)
        else:
            q = 'SELECT %s FROM %s' % (fieldlist, table)

        self.c.execute(q)
        self.conn.commit()

        res = self.c.fetchall()
        res = map(lambda l: dict(zip(fields, l)),res)
        return res

    @staticmethod
    def connect(self):
        db = SQLiteConn()
        return db

if __name__ == '__main__':
    db = SQLiteConn('db/french_window.db')
    fields = ('id','title','author_id', 'summary', 'publisher', 'is_series', 'series_nr', 'isbn13', 'isbn10', 'language')
    # db.select_all('books', fields, {})

    # db.update('books', 41, ('title','summary'),('john malkovich','is awesome'))
    # print len(db.select_all('books',fields,{'author_id':30}))

    # print db.search_all('books', fields, {'title':'eye'})
