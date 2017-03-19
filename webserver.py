import web
import lib
import config
import scan

# import decorators
from lib.auth import authenticated
from models import Book, Author, Series, Wishlist, BookWork
from lib.api import GoogleBooksAPI

from operator import attrgetter

import json

class WishlistPage(lib.webpage.Controller):
    model = Wishlist

urls = (
    '/', 'Index',
    '/books/', 'BookPages',
    '/books/(.*)/(.*)', 'BookPages',
    '/auth/(.+)/', 'AuthPages',
    '/ajax/(.+)/', 'Ajax',
    '/authors/(.+)/(.*)', 'AuthorPages',
    '/scan/(.+)/', 'scan.ScanPage',
    '/series/(.+)/(.*)', 'SeriesPage',
)

urls += WishlistPage.urls()
app = web.application(urls,globals())

# Setup session
class Session(web.session.Session):
    def _setcookie(self, session_id, expires='', **kw):
        if expires == '':
            expires = self._config.timeout

        super(Session, self)._setcookie(session_id, expires, **kw)

if web.config.get('_session') is None:
    store = web.session.DiskStore('sessions')
    session = Session(app,store)
    web.config._session = session
else:
    session = web.config._session

scan.session = session

# render = web.template.render('site/templates/', base='skeleton', globals={'session':session})
render = web.template.render('site/', base='base', globals={'session':session})

class Page(object):
    def __init__(self):
        self.auth = lib.auth.Authenticator(session)
        self.session = session

    def get_msg(self):
        data = web.input()
        if 'msg' in data.keys():
            return data['msg']
        return ''


    # Clean data - TODO change to decorator
    def inputdata(self):
        data = web.input()
        pdata = {}
        for (k,v) in data.items():
            pdata[k] = lib.util.html_sanitize(str(v))

        return pdata


class SeriesPage(lib.webpage.Controller):
    session = session
    model = Series

    def setUp(self):
        super(SeriesPage, self).setUp()

    @authenticated
    def view(self, o_id):
        series = super(SeriesPage, self).view_data(o_id)
        books = Book.select_all({'series_id':series.id})

        # sort books by series_nr
        books = sorted(books, key=attrgetter('series_nr'))

        return self.render.view(message=self.msg(), object=series, books=books)


class WishlistPage(lib.webpage.Controller):
    session = session
    model = Wishlist

    @authenticated
    def search_get(self):
        return self.render.search(self.msg())

    def _search(self):
        data = web.input()
        authorname = data['author_name']

        #define which filter to use
        if data['datefilter'] == 'upcoming':
            ffunc = lib.api.filters.upcoming
        else:
            ffunc = lib.api.filters.all

        books = Book.api_search(data['title'],authorname, filterf=ffunc)
        bws = BookWork.collect(books)

        return bws

    @authenticated
    def search_post(self):
        bws = self._search()
        return self.render.search_results(message=self.msg(), books=books)

    @authenticated
    def ajax_search(self):
        bws = self._search()
        #process dictionaries
        bwdicts = map(lambda l: l.json_parse(), bws)
        # print bwdicts
        return json.dumps(bwdicts)

    def setUp(self):
        super(WishlistPage, self).setUp()
        self.clearfunctions()
        self.functions['search'] = 'search'
        self.functions['add'] = 'add'
        self.functions['ajax_list'] = 'ajax_list'
        self.functions['ajax_delete'] = 'ajax_delete'
        self.functions['ajax_add'] = 'ajax_add'
        self.functions['ajax_search'] = 'ajax_search'


class Index(Page):
    def GET(self):
        data = web.input(msg='')
        if data.msg == '':
            msg = ''
        else:
            msg = '?msg='+data.msg

        return web.seeother('/books/list/' + msg)

class AuthorPages(Page):
    def GET(self, page=None, *args, **kwargs):
        if page is None: return self.list()
        elif page == 'list': return self.list()
        elif page == 'add' : return self.add()
        elif page == 'upcoming' : return self.upcoming()
        elif page == 'upcoming_books' : return self.upcoming_books_get(*args)

    def POST(self, page=None, *args, **kwargs):
        if page == 'upcoming_books' : return self.upcoming_books_post()

    @authenticated
    def list(self):
        data = web.input()
        authors = Author.select_all(Author.prune_fields(data))

        for a in authors:
            a.nbooks = a.nbooks()

        return render.list_authors(message=self.get_msg(), data=authors)

    @authenticated
    def add(self):

        data = web.input()
        if not('name' in data.keys() and 'author_add_form' in data.keys()):
            return render.add_author(message=self.get_msg())

        if data['id'] != '-1':
            err = "This author already exists in the database!"
            return render.add_author(message=err)

        a = Author.from_dict(data)
        a.save()

        msg = 'Successfully added author %s (id %s)' % (a.name, str(a.id))
        return web.seeother('/authors/list/?msg='+msg)

    @authenticated
    def upcoming(self):
        return render.authors_upcoming(message=self.get_msg())

    def upcoming_books_get(self, author_id=-1):
        if not str(author_id).isdigit():
            err = 'Invalid author'
            return web.seeother('/authors/upcoming/?msg=' + err)

        author = Author.select({'id':int(author_id)})

        if author is None:
            err = 'Invalid author'
            return web.seeother('/authors/upcoming/?msg=' + err)

        books = author.upcoming_books(author.name)
        return render.watchlist_add_books(message=self.get_msg(), books=books)

    def upcoming_books_post(self):
        data = web.input()
        author = Author.search_plus({'id':data['id'],'name':data['name']})
        books = author.upcoming_books(data['name'])
        return render.watchlist_add_books(message=self.get_msg(), books=books)

# BOOK CONTROLLERS
class BookPages(Page):
    def GET(self, page=None, *args,**kwargs):
        if page is None: return self.list_books()
        elif page == 'list': return self.list_books()
    	elif page == 'add' : return self.add_book_get()
        elif page == 'view' : return self.view_book(*args)
        elif page == 'edit' : return self.edit_book_get(*args)
        elif page == 'isbn' : return self.api_form()
        elif page == 'search' : return self.search()
        elif page == 'delete' : return self.delete_book(*args)

    def POST(self, page=None, *args, **kwargs):
        if page is None: return self.list_books()
        elif page == 'add' : return self.add_book_post()
        elif page == 'edit' : return self.edit_book_post(*args)
        elif page == 'delete' : return self.delete_book()
        elif page == 'isbn' : return self.api_fetch()
        elif page == 'ajax_save' : return self.ajax_save()

    @authenticated
    def list_books(self):
    	data = dict(web.input())

        # process any filters if required
        data['user_id'] = session.user_id
        data['in_library'] = 1

        msg = self.get_msg()
        books = Book.select_all(Book.prune_fields(data))

        return render.list_books(message=msg, books=books)

    @authenticated
    def view_book(self,book_id=None):

        if book_id is None or not(book_id.isdigit()):
            errormsg = 'No valid identifier specified'
            return web.seeother('/?msg='+errormsg)

        book = Book.select({'id':int(book_id)})

        if book is None:
            errormsg = 'Book ID not found'
            return web.seeother('/?msg='+errormsg)

        if book.user_id != session.user_id:
            err = 'ERR - not yours to view'
            return web.seeother('/?msg' + err)

        return render.view_book(message='', book=book)

    @authenticated
    def add_book_get(self):
        return render.add_book(message="", prefill=None,edit=False)

    @authenticated
    def _add_book(self):
        # data = dict(web.input())
        data = self.inputdata()
        book = Book.from_dict(data)

        author = Author.search_plus({'id':data['author_id'],'name':data['authors.name']})

        book.author = author
        book.author_id = author.id

        book.user_id = session.user_id

        if (data['is_series'] == 'True'):
            book.is_series = True
            series = Series.search_plus({'id':data['series_id'], 'name':data['series.name']})
            book.series = series
            book.series_id = series.id
        else:
            book.is_series = False
            book.series = None

        uid = book.save()
        msg = 'Book added to your library!'

        # remove book from wishlist
        wishes = Wishlist.select_all({'user_id':session.user_id})
        matched_wishlist = filter(lambda l: l.matchbook(book), wishes)

        if len(matched_wishlist) > 0:
            msg = 'Book added to your library & removed from the wishlist!'
            for w in matched_wishlist:
                w.delete()

        return (msg, book)

    @authenticated
    def add_book_post(self):
        (msg, book) = self._add_book()
        return web.seeother('/books/list/?msg='+lib.util.url_encode(msg))


    @authenticated
    def ajax_save(self):
        (msg, book) = self._add_book()
        return json.dumps({'msg':msg, 'book':book.json_parse()})


    @authenticated
    def edit_book_get(self,book_id=None):
        if book_id is None or not(book_id.isdigit()):
            errormsg = 'No valid identifier specified'
            return web.seeother('/books/list/?msg='+errormsg)

        #get book data
        book = Book.select({'id':int(book_id)})

        if book.user_id != session.user_id:
            msg = 'ERR - Not yours to update'
            return web.seeother('/books/list/?msg=' + msg)

        if book is None:
            errormsg = 'No valid identifier specified'
            return web.seeother('/books/list/?msg='+errormsg)

        #unquote stuff
        print book.summary
        book.summary = web.net.htmlunquote(book.summary)
        print book.summary

        return render.add_book(message='', prefill=book, edit=True)

    @authenticated
    def edit_book_post(self, book_id=None):
        data = self.inputdata()

        # get original book
        if book_id is None or not(book_id.isdigit()):
            err = 'ERR - Invalid book identifier'
            return web.seeother('/books/list/?msg=' + err)
        book = Book.select({'id':int(book_id)})

        if book.user_id != session.user_id:
            err = 'ERR - Not yours to update'
            return web.seeother('/books/list/?msg=' + err)

        book.update(data)

        if (data['is_series'] == 'True'):
            book.is_series = True
            series = Series.search_plus({'id':data['series_id'], 'name':data['series.name']})
            book.series = series
        else:
            book.is_series = False
            book.series = None

        book.save()
        return web.seeother('/books/view/'+str(book.id))

    @authenticated
    def delete_book(self, get_id=-1):
        if get_id != -1:
            book_id = get_id
        else:
            book_id = web.input().id

        b = Book.select({'id':book_id})

        target = '/books/list/'
        msg = ''

        if b is None:
            msg = 'ERR - Book does not exist'
        else:
            if b.user_id != session.user_id:
                msg = 'ERR - Not yours to delete'
            else:
                Book.delete_id(int(book_id))
                msg = 'Book deleted successfully'

        return web.seeother('%s?msg=%s' % (target, msg))

    @authenticated
    def api_form(self):
        return render.api_search(message='')

    @authenticated
    def api_fetch(self):
        data = dict(web.input())
        isbn = data['isbn13']
        api = GoogleBooksAPI('randomkey')
        data = api.search_isbn(isbn)

        book = Book.parse_from_api(api, data)


        if book is None:
            msg = 'Book not found - please enter data manually'
        else:
            # Look up author
            author = Author.select({'name':book.author_name})

            if author is not None:
                book.author = author
                book.author_name = None

            msg = 'Book found in google DB - please confirm the data'

        return render.add_book(message=msg, prefill=book, edit=False)

    @authenticated
    def search(self):
        data = web.input();

        valid_keys = ('title',)
        search_keys = dict(filter(lambda (k,v): k in valid_keys, data.items()))

        if len(search_keys) == 0:
            # return standard search form
            return render.search_book(message='')
        else:
            # do search
            books = Book.search(exact={'user_id':session.user_id}, approx=search_keys)
            return render.list_books(message='', books=books)





class Ajax(Page):
    @authenticated
    def GET(self, page):
        pass

    @authenticated
    def POST(self, page):
        if page == 'search_author':
            return self._search_author()
        if page == 'search_series' :
            return self._search_any(Series, 'name')
        if page == 'upcoming' :
            return self._upcoming_books()

    def _search_author(self):
        data = web.input()
        authors = Author.search(approx={'name':data.query})
        resp = {}
        authorlist = map(lambda l: {'data':l.id, 'value':l.name}, authors)
        resp['suggestions'] = authorlist
        return json.dumps(resp)

    def _search_series(self):
        data = web.input()
        series = Series.search(approx={'name':data.query})
        resp = {}
        slist = map(lambda l: {'data':l.id, 'value':l.name}, series)
        resp['suggestions'] = slist
        return json.dumps(resp)

    def _search_any(self, cls, key='name'):
        data = web.input()
        res = cls.search(approx={key:data.query})
        outp = {}
        rlist = map(lambda l: {'data':l.pk(), 'value':eval('l.'+key)}, res)
        outp['suggestions'] = rlist
        return json.dumps(outp)

    def _upcoming_books(self):
        data = web.input()
        books = Author.upcoming_books(data['name'])
        dictlist = map(lambda l: l.__dict__, books)
        return json.dumps(dictlist)

# AUTH CLASSES
class AuthPages(Page):
    def GET(self, page):
        if page == 'login': return self.login_get()
        if page == 'logout' : return self.logout()

    def POST(self, page):
        if page == 'login' : return self.login_post()

    def login_get(self):
        msg = self.get_msg()
        return render.login(message=msg)

    def login_post(self):
        target = '/books/'
        msg = ''
        data = web.input()
        u = self.auth.login(data['username'],data['password'])
        if u is not None:
            if u.is_authenticated():
                session.user = u.name
                session.user_level = u.level
                session.user_id = u.id
                session.is_authenticated = True
                msg = 'Successfully logged in!'
                if 'redirect' in data.keys():
                    target = data['redirect']
            else:
                msg = 'Wrong username/password; please enter correct login details'
        else:
            msg = 'Username not found; please enter a correct username'

        return web.seeother('%s?msg=%s' % (target, msg))

    def logout(self):
        session.kill()
        return web.seeother('/auth/login/')

#AUTHOR CONTROLLERS
class list_authors(Page):
    def GET(self):
        msg = self.get_msg()
        return render.list_authors(message=msg,authors=authors)


if __name__ == "__main__":
    app.run()
