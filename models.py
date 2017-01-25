import lib
from lib.db.dbschema import Schema
from lib.db import get_db

import datetime



import json, pprint

# Not a DB storage object
class BookWork(lib.models.Model):
    def __init__(self, book):
        self.associated_books = [book]
        self.primary_book = book
        self._setup_fields()

    def _update(self):
        self._define_primary_book()
        self._setup_fields()

    def _define_primary_book(self):
        for b in self.associated_books:
            if len(b.summary) > len(self.primary_book.summary):
                self.primary_book =  b

    def _setup_fields(self):
        pb = self.primary_book
        self.title = pb.title
        self.author = pb.author
        self.author_id = pb.author.id
        self.publish_date = pb.publish_date
        self.summary = pb.summary
        self.image_link = pb.image_link

    def add(self, book):
        self.associated_books.append(book)
        self._update()

    def nbooks(self):
        return len(self.associated_books)

    def __str__(self):
        return "Bookwork: %s by %s, (%d books)" % (self.title, self.author.name, self.nbooks())

    @staticmethod
    def collect(books):
        # compute title & author similarity matrix
        m = [0]*len(books)

        for i in range(0,len(books)):
            m[i] = [0]*len(books)
            m[i][i] = True
            for j in range(i+1, len(books)):
                m[i][j] = books[i].matchbook(books[j])

        works = []

        for i in range(0,len(books)):
            # if book has property
            work = getattr(books[i], 'bookwork', None)
            if work is None:
                # create a new bookwork
                bw = BookWork(books[i])
                works.append(bw)
                # for each book, add it to this bookwork
                for j in range(i+1,len(books)):
                    if m[i][j]:
                        bw.add(books[j])
                        books[j].bookwork = bw

        return works


class Book(lib.models.Model):
    @classmethod
    def set_schema(cls):
        schema = Schema(Book)
        schema.table = 'books'
        schema.primary_key = 'id'
        schema.input_fields = ['title','author_id', 'user_id', 'series_id', 'summary', 'publisher', 'publish_date', 'is_series', 'series_nr', 'isbn13', 'isbn10', 'language', 'in_library']
        schema.auto_fields = ['id', 'time_created']
        schema.link_to_object('author_id', Author)
        schema.link_to_object('user_id', lib.auth.User)
        schema.link_to_object('series_id', Series)
        return schema

    def __init__(self):
        self.title = 'n/a'
        self.author = None
        self.author_id = None
        self.author_name = None
        self.summary = 'n/a'
        self.publisher = 'n/a'
        self.isbn13 = 'n/a'
        self.isbn10 = 'n/a'
        self.language = 'en'
        self.series = None
        self.series_id = -1
        self.is_series = False
        self.series_nr = 1
        self.id = None

    def __str__(self):
        return "'%s' by %s. (ISBN: %s)" % (self.title, self.author.name, self.isbn13)

    @staticmethod
    def parse_from_api(api, data):
        book = Book()
        b = api.parse_book(book, data)
        return b

    @staticmethod
    def api_search(title='', authorname='', onepage=True, filterf=lib.api.filters.all):
        api = lib.api.GoogleBooksAPI()

        # build query
        params = {}
        if title == '' and authorname is not '':
            params['q'] = 'inauthor:"%s"' % (authorname)
        elif title != '' and authorname is '':
            params['q'] = 'intitle:' + title
        elif title != '' and authorname is not '':
            params['q'] = 'intitle:%s+inauthor:%s' % (title, authorname)
        elif title == '' and authorname is '':
            return []

        params['orderBy'] = 'newest'
        params['langRestrict'] = 'en'

        if onepage:
            booklist = api.peel(Book, params, filterf=filterf, step=30,cap=20)
        else:
            booklist = api.peel(Book, params, filterf=filterf, step=30)

        for b in booklist:
            b.author = Author.search_plus({'name':b.author_name})

        return booklist

    def matchbook(self, book):
        titlematch = lib.util.issimilar(self.title, book.title)
        authormatch = lib.util.issimilar(self.author.name, book.author.name)
        return titlematch & authormatch




class Author(lib.models.Model):
    @classmethod
    def set_schema(cls):
        schema = Schema(cls)
        schema.table = 'authors'
        schema.primary_key = 'id'
        schema.input_fields = ['name']
        schema.auto_fields = ['id']
        return schema

    def __init__(self):
        self.name = ''
        self.isbn_id = ''
        self.id = None

    # TODO
    def get_books(self):
        books = Book.find_all({'author_id':self.id})
        print len(books)
        print map(str,books)

    def __str__(self):
        return '%s (%s)' % (self.name, str(self.id))

    def nbooks(self):
        return get_db().count(Book.schema, {'author_id':self.id})

    def upcoming_books(self):
        api = lib.api.GoogleBooksAPI()

        # build query
        params = {}
        params['q'] = 'inauthor:' + self.name
        params['orderBy'] = 'newest'
        params['langRestrict'] = 'en'

        # filterfunc
        def ffunc(book):
            release = datetime.datetime.strptime(book.publish_date, '%Y-%m-%d')
            today = datetime.datetime.today()
            return release > today

        booklist = api.peel(Book, params, filterf=ffunc, step=30)

        for b in booklist:
            b.author = self

        return booklist


class Series(lib.models.Model):
    def __init__(self):
        self.name = ''
        self.id = None
        self.description = ''

    @classmethod
    def set_schema(cls):
        schema = Schema(cls)
        schema.table = 'series'
        schema.primary_key = 'id'
        schema.input_fields = ['name', 'description']
        schema.auto_fields = ['id']
        return schema

    def __str__(self):
        return self.name + ' (' + str(self.id) + ')'


class Wishlist(lib.models.Model):
    def __init__(self):
        self.id = None
        self.user_id = None
        self.author_id = None
        self.notes = ''
        self.summary = ''
        self.publish_id = ''

    @classmethod
    def set_schema(cls):
        schema = Schema(cls)
        schema.table = 'wishlist'
        schema.primary_key = 'id'
        schema.input_fields = ['user_id', 'author_id', 'title', 'publish_date', 'summary','notes']
        schema.auto_fields = ['id', 'time_created']
        schema.link_to_object('user_id', lib.auth.User)
        schema.link_to_object('author_id', Author)
        return schema


    def __str__(self):
        return 'Wish I had ' + self.title+ ' by ' + self.author.name


    # Returns if this wishlist item sufficiently matches the book object
    # Comparing only title & author
    # Uses string matching utility
    def matchbook(self, book):
        titlematch = lib.util.issimilar(self.title, book.title)
        authormatch = lib.util.issimilar(self.author.name, book.author.name)
        print 'Title match %s; Author match %s' % (str(titlematch), str(authormatch))
        return titlematch & authormatch



Book.schema = Book.set_schema()
Author.schema = Author.set_schema()
Series.schema = Series.set_schema()
Wishlist.schema = Wishlist.set_schema()

if __name__ == '__main__':
    books = Book.api_search(authorname='Fredrik Backman', filterf=lib.api.filters.upcoming )
    works = BookWork.collect(books)
    # for w in works:
    #     print w

    parsed = []
    for w in works:
        parsed.append(w.json_parse())

    pp = pprint.PrettyPrinter()
    pp.pprint(json.dumps(parsed))

