# defines a JSON API exposing minimal functionality of the webserver
import web
from lib.api import GoogleBooksAPI
from models import Book, Author

import json
import pprint

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
        return ''

    def isbn_lookup(self):
        # ctx = web.ctx
        # env = web.ctx.env.get('CONTENT_TYPE')

        # pp = pprint.PrettyPrinter()
        # pp.pprint(env)
        # pp.pprint(dict(ctx))

        data = web.input()
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



urls = ('/(.*)', 'MyAPI')

if __name__ == '__main__':
    app = web.application(urls, globals())
    app.run()

