import lib, web
from PIL import Image
import zbar, cv2, io
import json
from models import Book, Author

session = None

class ScanPage(lib.webpage.Controller):
    def setUp(self):
        self.session = session
        self.render = web.template.render('site/scan/', base='../base', globals={'session':self.session})
        self.auth = lib.auth.Authenticator(self.session)
        self.clearfunctions()
        self.functions = {
                    'ajax_process' : 'ajax_process',
                    'scan': 'scan',
                    'ajax_bookdata' : 'ajax_bookdata'}


    def scan(self):
        return self.render.scan(message=self.msg())

    def ajax_process(self):
        data = web.input()
        imgdata = data.imgdata
        encoding = data.encoding
        format = data.format

        assert encoding == 'base64' and format == 'image/png'

        # encode as image
        # img = open('img/snapshots/snapshot.png', 'wb')
        # img.write(imgdata.decode('base64'))
        # img.close()

        # lib.util.Image.snapstore('snapshot_', imgdata, encoding, format)
        decoded = lib.util.Image.decode(imgdata, encoding)
        img = Image.open(io.BytesIO(decoded)).convert('L')

        bcscanner = Scanner()
        res = bcscanner.scan(img)

        jdump = json.dumps({'hits' : len(res), 'data':res})
        return jdump


    def ajax_bookdata(self):
        data = dict(web.input())
        isbn = data['key']
        api = lib.api.GoogleBooksAPI()
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
        jdump = json.dumps(book.json_parse())
        return jdump


class Scanner(object):
    def __init__(self):
        self.img_scanner = zbar.ImageScanner()
        # self.img_scanner.parse_config('disable')
        self.img_scanner.parse_config('isbn10.enable')
        self.img_scanner.parse_config('isbn13.enable')
        # check C source for full ENUM - see http://zbar.sourceforge.net/api/zbar_8h.html


    def imgscan(self, img_loc):
        pil = Image.open(img_loc).convert('L')  #Convert to grayscale
        self.scan(pil)

    # Assumes a grayscale picture in PIL object
    def scan(self, pil):
        (w,h) = pil.size
        data = pil.tobytes()
        img = zbar.Image(w,h,'Y800',data)
        self.img_scanner.scan(img)

        symbolreturns = []
        for symbol in img:
            if 'ISBN' in str(symbol.type):
                symbolreturns.append({'type': str(symbol.type), 'value': str(symbol.data)})
                print symbol.type, ": ", symbol.data

        return symbolreturns


class VideoStream(object):
    def __init__(self, scanf):
        self.scanf = scanf

    def load_stream(self, stream):
        pass

    def load_movie(self, stream):
        pass

    def streamcap(self, vid):
        cap = cv2.VideoCapture(vid)
        fcounter = 0
        while (cap.isOpened()):
            (r, frame) = cap.read()
            if not r:
                break
            grayframe = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Parsing now
            self.parse(grayframe)
            # continue display
            cv2.imshow('frame', grayframe)

            if (cv2.waitKey(1)) & 0xFF == ord('q'):
                break
            fcounter += 1

        cap.release()
        cv2.destroyAllWindows()
        print fcounter

    def parse(self, arr):
        pil = Image.fromarray(arr)
        self.scanf(pil)


if __name__ == '__main__':
    scanner = Scanner()
    scanner.imgscan('img/examples/test1.jpg')
    # vs = VideoStream(scanner.scan)
    # # vs.streamcap('img/videos/video1.mov')
    # vs.streamcap(1)
    # print 'done'

