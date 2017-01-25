import unittest

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.db.dbschema import Schema
import models


class TestSchema(unittest.TestCase):
    def setUp(self):
        b = Schema(models.Book)
        b.table = 'books'
        b.primary_key = 'id'
        b.input_fields = ['title', 'author_id']
        b.auto_fields = ['id']
        b.link_to_object('author_id', models.Author)
        self.b = b

        a = Schema(models.Author)
        a.table = 'authors'
        a.primary_key = 'id'
        a.input_fields = ['name']
        self.a = a

    def tearDown(self):
        pass

    def test_definitions(self):
        self.assertTrue(self.a.is_valid())
        self.assertTrue(self.b.is_valid())
        self.assertEquals(self.a.table, 'authors')

    def test_fields(self):
        self.assertEquals(len(self.b.fields()),3)
        self.assertTrue('id' in self.b.fields())
        self.assertTrue('author_id' in self.b.fields())
        self.assertTrue('title' in self.b.fields())

        self.assertEquals(len(self.b.fields(True)),3)
        self.assertTrue('books.id' in self.b.fields(True))
        self.assertTrue('books.author_id' in self.b.fields(True))
        self.assertTrue('books.title' in self.b.fields(True))

    def test_full_view(self):
        fields = ['books.author_id', 'books.id', 'books.title', 'authors.name', 'authors.id']
        table = '( books JOIN authors ON books.author_id = authors.id )'
        self.assertEquals(self.b.full_view(), (table, fields))


if __name__ == '__main__':
    # models.Book.schema
    # models.Author.schema
    unittest.main()

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TestSchema)
