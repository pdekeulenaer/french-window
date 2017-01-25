import unittest

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.db import get_db
import models



class TestDB(unittest.TestCase):
    def setUp(self):
        self.b = models.Book()
        self.a = models.Author()
        self.db = get_db()

    def tearDown(self):
        pass

    def test_select_one(self):
        db = self.db
        res = db.select(models.Book.schema, {'books.id' : 46})
        prefix = models.Book.schema.table
        self.assertEquals(res[prefix + '.id'], 46)
        self.assertEquals(res[prefix + '.title'],'The Penguin Lessons')
        self.assertEquals(res[prefix + '.author_id'],29)

        res = db.select(models.Book.schema, {'books.title' : 'The Penguin Lessons', 'books.id' : 46})
        prefix = models.Book.schema.table
        self.assertEquals(res[prefix + '.id'], 46)
        self.assertEquals(res[prefix + '.title'],'The Penguin Lessons')
        self.assertEquals(res[prefix + '.author_id'],29)

        res = db.select(models.Book.schema, {'books.title' : 'The Penguin Lessons', 'books.id' : 12})
        self.assertEquals(res, None)
        # pass

    def test_select_n(self):
        db = self.db
        res = db.select_all(models.Book.schema, {'books.author_id' : 30})
        prefix = models.Book.schema.table
        self.assertEquals(len(res), 3)
        self.assertEquals(res[0]['books.id'], 48)
        self.assertEquals(res[2]['books.title'], 'The Eye of the World')
        # pass

        res = db.select_all(models.Author.schema, {'authors.name': 'megmeg'})
        self.assertEquals(res, [])

    def test_store(self):
        db = self.db
        uid = db.store(models.Book.schema, {'title':'Test Book', 'author_id':'33', 'summary':'', 'isbn10':123456, 'isbn13':12345679, 'publisher':'PDK', 'language':'en'})
        res = db.select(models.Book.schema, {'books.id' : uid})
        self.assertEquals(res['books.title'], 'Test Book')

    def test_delete(self):
        db = self.db
        nres = len(db.select_all(models.Book.schema, {'books.title': 'Test Book'}))
        uid = db.delete(models.Book.schema, [('title', '=', 'Test Book')])
        nres2 = len(db.select_all(models.Book.schema, {'books.title': 'Test Book'}))
        self.assertEquals(nres-1, nres2)

    def test_update(self):
        db = self.db
        uid = db.select(models.Book.schema, {'books.title':'Test Book'})['books.id']
        db.update(models.Book.schema, uid, {'publisher': 'Johnny Boy'})
        res = db.select(models.Book.schema, {'books.id' : uid})
        self.assertEquals(res['books.publisher'], 'Johnny Boy')

    def test_search(self):
        db = self.db
        res = db.search(models.Book.schema, {'books.title': 'book', 'authors.name': 'philip'})
        self.assertEquals(len(res), 2)
        self.assertEquals(res[0]['authors.name'], 'Philip De Keulenaer')
        self.assertEquals(res[1]['books.title'], 'Book 2')



def suite():
    db_suite =  unittest.TestLoader().loadTestsFromTestCase(TestDB)

    return unittest.TestSuite([db_suite])


if __name__ == '__main__':
    unittest.main()

