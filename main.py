import models
from api import GoogleBooksAPI

def testAPI(isbn):
    api = GoogleBooksAPI('randomkey')
    data = api.search_isbn(isbn)
    book = models.Book.parse_from_api(api, data)
    return book

if __name__ == '__main__':
    # res = models.Book.find_exact({'id':10})
    # print res.title
    isbn = '9780099513780'
    # isbn = '9781447252245' # does not work yet :(
    b = testAPI(isbn)
    print b
    b.save()
