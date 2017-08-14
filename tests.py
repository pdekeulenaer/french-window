import pprint
from lib.db import get_db
import models
import lib
import config

schema = models.Book.schema

db = lib.db.sqlite_db_obj.Connection('data/test_french_window.db')
a = lib.db.sqlite_db_obj.Select(models.Book.schema)


a.add_filter('user_id', 2)
a.add_filter('title', 'i', False)
a.add_sort('series_id')
a.add_sort('title', False)
a.fields = ['books.id','books.title','books.user_id','users.name']

res = db.execute(a)

# for i in res:
#     print i
#     print "-------------------------------"


db = get_db()

vm = {'user_id':2}

resa = db.select(models.Book.schema, vm,True)
resb = db._select(models.Book.schema, vm,True)

print (resa)
print (resb)
