import unittest
import random

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import lib
import models
import config


class TestBook(unittest.TestCase):
    def setUp(self):
        self.b = models.Book()
        self.a = models.Author()

    def tearDown(self):
        pass

    def test_book_schema(self):
        self.assertEquals(self.b.pk(),self.b.id)

    def test_book_find(self):
        book = models.Book.select({'id':46})
        self.assertEquals(book.title, 'The Penguin Lessons')
        self.assertEquals(book.isbn10, '1405921803')
        self.assertEquals(book.author_id, 29)
        self.assertEquals(book.author.id, 29)
        self.assertEquals(book.author.name, 'Tom Michell')


    def test_book_find_all(self):
        books = models.Book.select_all({'authors.name': 'Philip De Keulenaer'})
        self.assertEquals(len(books), 3)
        self.assertEquals(books[0].title, 'Book 1')
        self.assertEquals(books[1].title, 'Book 2')
        self.assertEquals(books[1].author.id, 30)
        self.assertEquals(books[2].title, 'The Eye of the World')
        self.assertEquals(books[2].publisher, 'Orbit Books')

    def test_save_new(self):
        b = models.Book()
        b.title = 'Philip writes a book'
        b.author = models.Author()
        b.author.name = 'Meghana Manickam'
        b.user_id = 1
        uid = b.save()

        bb = models.Book.select({'id' : uid})
        self.assertEquals(bb.title, b.title)
        self.assertEquals(bb.author.name, b.author.name)

    def test_save_update(self):
        n = 'a' + str(random.randint(0,10000))
        b = models.Author.select({'id':32})
        b.name = n
        b.save()
        b2 = models.Author.select({'id':32})
        self.assertEquals(b2.name, n)

    def test_delete(self):
        authors = models.Author.select_all({'authors.name':'Meghana Manickam'})
        n1 = len(authors)
        for a in authors:
            a.delete()

        authors = models.Author.select_all({'authors.name':'Meghana Manickam'})
        self.assertEquals(len(authors), 0)

    def test_search(self):
        books = models.Book.search({'title' : 'Book', 'authors.name': 'philip'})
        self.assertEquals(books[0].author.name, 'Philip De Keulenaer')
        self.assertEquals(books[1].title, 'Book 2')



def suite():
    book_suite =  unittest.TestLoader().loadTestsFromTestCase(TestBook)
    return unittest.TestSuite([book_suite])

if __name__ == '__main__':
    unittest.main()
