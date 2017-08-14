# defines a JSON API exposing minimal functionality of the webserver
import web
from lib.api import GoogleBooksAPI
from models import Book, Author, Wishlist, Series
import lib

import json
import pprint
import hashlib

class MyAPI(object):
    def __init__(self):
        pass

    def GET(self, page=None):
        return self._handlereq(page)

    def POST(self, page=None):
        return self._handlereq(page)

    def _handlereq(self, page=None):
        print page
        if page is None: return 'N/A'
        elif page.startswith('isbn_lookup') : return self.isbn_lookup()
        elif page.startswith('add_book') : return self.add_book()
        elif page.startswith('test_auth') : return self.test_auth()

        return ''


    # TODO - make it so I can reuse from webserver
    def add_book(self):
        # bookcontroller = webserver.BookPages()
        data = web.input()

        u = self.authenticate(data, 'add_book')
        if not u.is_authenticated():
            return json.dumps({'error':'Not authenticated'})

        bookdata_temp = json.loads(data.data)
        bookdata = {}

        for el in bookdata_temp.keys():
            bookdata[el] = lib.util.html_sanitize(bookdata_temp[el])

        print lib.util.html_sanitize(bookdata['summary'])

        (msg, book) = self._add_book(u, bookdata)

        if book is not None:
            return json.dumps({'msg':msg, 'book':book.json_parse()})
        else:
            return json.dumps({'msg':msg})


    # backend of book adding
    def _add_book(self, user, data):
        book = Book.from_dict(data)

        print '---------------------------------'
        print data

        author = Author.search_plus({'name':data['author_name']})


        book.author = author
        book.author_id = author.id

        book.user_id = user.id

        if (data['is_series']):
            print "ADDING SERIES"
            book.is_series = True
            series = Series.search_plus({'name':data['series_name']})
            book.series = series
            book.series_id = series.id
        else:
            book.is_series = False
            book.series = None

        # temp hack
        book.in_library = 1

        uid = book.save()
        msg = 'Book added to your library!'

        # remove book from wishlist
        wishes = Wishlist.select_all({'user_id':user.id})
        matched_wishlist = filter(lambda l: l.matchbook(book), wishes)

        if len(matched_wishlist) > 0:
            msg = 'Book added to your library & removed from the wishlist!'
            for w in matched_wishlist:
                w.delete()

        return (msg, book)




    def isbn_lookup(self):
        # ctx = web.ctx
        # env = web.ctx.env.get('CONTENT_TYPE')

        # pp = pprint.PrettyPrinter()
        # pp.pprint(env)
        # pp.pprint(dict(ctx))

        payload = web.input()
        data = json.loads(payload.data)
        if 'isbn' not in data.keys():
            return json.dumps({'error':'No ISBN code specified'})
        isbn = data['isbn']
        api = GoogleBooksAPI()
        googledata = api.search_isbn(isbn)

        print googledata

        book = Book.parse_from_api(api, googledata)

        if book is None:
            return json.dumps({'error':'Book not found'})
        else:
            # Look up author
            author = Author.select({'name':book.author_name})

            if author is not None:
                book.author = author
                book.author_name = None

            return json.dumps({'book':book.json_parse()})

    def test_auth(self):
        u = self.authenticate(web.input(), 'test_auth')
        print u.is_authenticated()
        print u
        return json.dumps({'success':u.is_authenticated()})



    def authenticate(self, data, resource):
        if 'auth' not in data.keys():
            return None
        authobj = json.loads(data.auth)

        # get the fields under auth
        # user, challenge, hash, resource, digest
        # protocol hashes the following string:username+resource+digest+challenge+secret
        # where:
        #   secret is the sha256 of the user's pw
        #   digest is the digest of the 'data' object in the request, sha256 hex

        # to verify I need to query the users' pw, reconstruct the hash and verify it is the same
        userobj = lib.auth.User.select({'name':authobj['user']})
        datastr = data.data
        datadigest = hashlib.sha256(datastr).hexdigest()

        # print 'pw:       ' + userobj.password
        # print 'data:     '  + datastr
        # print 'data dig: ' + datadigest


        hashinput = '%s+%s+%s+%s+%s' % (authobj['user'], resource, datadigest, authobj['challenge'], userobj.password)
        hashstr = hashlib.sha256(hashinput).hexdigest()

        # print 'input: ' + hashinput
        # print 'reconstructed: ' + hashstr
        # print 'Original copy: ' + authobj['hash']

        if hashstr == authobj['hash']:
            userobj._is_authenticated = True

        return userobj


urls = ('/(.*)', 'MyAPI')

if __name__ == '__main__':
    app = web.application(urls, globals())
    app.run()

