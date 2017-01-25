import json, pprint
import urllib, urllib2
import re
import filters

class API(object):
    def search_isbn(self, isbn):
        print 'Not yet implemented'

    def search_author(self, author):
        print 'Not yet implemented'

    def setkey(self, key):
        self.key = key

class GoogleBooksAPI(object):
    def __init__(self, key=None):
        if key is None:
            self.key = 'AIzaSyBUPyNKvbK6RwVSf0jNqsUkHrjBmW_TM4M'
        else:
            self.key = key
        self.endpoint = 'https://www.googleapis.com/books/v1/volumes'

    # returns a Book object with necessary information
    def search_isbn(self, isbn):
        q = '%s?q=isbn:%s&api_key=%s' % (self.endpoint, isbn, self.key)
        response = urllib2.urlopen(q)
        data = json.load(response)
        return data

    def search_author(self, name, lang='en'):
        filters = {}
        filters['q'] = 'inauthor:' + name
        filters['orderBy'] = 'newest'
        if lang in ['en','fr'] :  filters['langRestrict'] = lang
        return self.fetch(self.buildq(dict(filters)))
        # q = '%s?%s&api_key=%s' % (self.endpoint, qstring, self.key)

    def peel(self, cls, params, filterf=filters.all, step=10, cap=250):
        start = 0
        hasnext = True
        nbooks = 0
        cap = min(cap, 500)
        bookdata = []

        while hasnext:
            params['startIndex'] = start
            params['maxResults'] = step
            q = self.buildq(params)
            data = self.fetch(q)

            hasnext = 'items' in data.keys();

            if hasnext:
                nbooks += len(data['items'])
                books = data['items']
                for el in books:
                    book = self.parse_book(cls(), el)
                    if filterf is None or (filterf(book)):
                        bookdata.append(book)

            start += step

            if start > cap:
                hasnext = False


            # a = raw_input()

        # filter book output
        # uniquebooks = set(bookdata)
        return bookdata


    def buildq(self, paramdict):
        q = urllib.urlencode(paramdict)
        return q

    def fetch(self, q):
        url = '%s?%s&key=%s' % (self.endpoint, q, self.key)
        response = urllib2.urlopen(url)
        data = json.load(response)
        return data

    @staticmethod
    def parse_book(book, data):
        # pp = pprint.PrettyPrinter()

        if 'items' not in data.keys():
            if 'volumeInfo' in data.keys():
                bookdata = data['volumeInfo']
            else:
                return None
        else:
            books = data['items']
            assert len(books) == 1
            bookdata = books[0]['volumeInfo']

        # set the values
        book.title = bookdata.setdefault('title','unknown title')
        book.author_name = bookdata.setdefault('authors', ['unknown author'])[0]
        book.publisher = bookdata.setdefault('publisher','')
        book.summary = bookdata.setdefault('description','')
        book.language = bookdata.setdefault('language','')
        # book.is_series = False
        # book.series_nr = 'n/a'

        # Temp values
        book.image_link = '/static/jpg/no-image-available.jpg'
        if 'imageLinks' in bookdata.keys():
            book.image_link = bookdata['imageLinks']['thumbnail']

        # Convert publication date - YYYY-MM-DD
        rawdate = re.sub("[^0-9\-]", '', bookdata.setdefault('publishedDate','1900-1-1'))
        pubdates = map(int, rawdate.split('-')) # convert to a list of ints
        mask = [0,0,0]
        for i in range(0,len(pubdates)):
            mask[i] = pubdates[i]

        pubdates = map(max, zip(mask, [1900,1,1])) # fix occasions where not a full date is given
        book.publish_date = '-'.join(map(str,pubdates))

        # parse ISBNs
        identifiers = bookdata.setdefault('industryIdentifiers',[])
        for identifier in identifiers:
            if identifier['type'] == 'ISBN_13':
                book.isbn13 = identifier['identifier']
            if identifier['type'] == 'ISBN_10':
                book.isbn10 = identifier['identifier']

        # pp.pprint(identifiers)
        return book


if __name__ == '__main__':
    pp = pprint.PrettyPrinter()
    api = GoogleBooksAPI()
    filters = {}
    filters['q'] = 'inauthor:jeffrey archer'
    filters['orderBy'] = 'newest'
    filters['langRestrict'] = 'en'

    class Book:
        pass

    data = api.peel(Book, filters, step=30, cap=150)



    def filterdate(datum):
        (title, isbn, date) = datum
        splits = date.split("-")
        year = splits[0]
        # month = splits[1]
        # day = splits[2]
        return int(year) == 2017

    fdata = filter(filterdate,data)

    pp.pprint(fdata)
