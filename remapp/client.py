import urllib, urllib2
import config
import json

class Client(object):
    def __init__(self):
        self.url = config.api_hook
        self.parser = JsonParser()


    def isbn_lookup(self, isbn):
        return self.request('isbn_lookup', {'isbn': isbn})

    def request(self, resource, data):
        data = urllib.urlencode(data)
        resp = urllib2.urlopen(url=(self.url+resource), data=data).read()

        return self.parser.parse(resp)


class Parser(object):
    def __init__(self):
        pass

    def parse(self, resp):
        return 'Parse method must be overridden'

class JsonParser(Parser):
    def parse(self, resp):
        return json.loads(resp)




if __name__ == '__main__':
    c = Client()
    data = c.isbn_lookup('9780817405021')
    print type(data)
    print data
