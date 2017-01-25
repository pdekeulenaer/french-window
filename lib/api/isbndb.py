# ISBN API access
import json, pprint
import urllib2

class ISBN():
    def __init__(self, key):
        # configurations
        self.key = key
        self.json_endpoint = 'http://isbndb.com/api/v2/json/%s/' % (key)

    # define requests
    def book(self, isbn):
        url = (self.json_endpoint + 'book/%s') % (isbn)
        resp = json.load(urllib2.urlopen(url))
        data = resp['data']
        return data

    def process_book(self, isbn):
        pass




if __name__ == '__main__':
    key = 'DZKIDUK0'
    api = ISBN(key)

    isbn = '9780345521316'
    # isbn = '9780356503820' #not found (wheel of time)
    data = api.book(isbn)

    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(data)
