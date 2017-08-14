import zbar, cv2
from PIL import Image
from PIL import ImageTk

class Viewer:
    def __init__(self, windowname='Preview Window', feed=1):
        self.windowname = windowname
        self.feed = feed
        self.capture = None
        self.vidstream = None

        #initialize scanner
        self.scanner = Scanner()

        # set processing function
        def testproc(key):
            print key

        self.process_func = testproc

    def start(self, w=800,h=600):
        self.vidstream = cv2.VideoCapture(self.feed)
        self.vidstream.set(3,w)
        self.vidstream.set(4,h)


    def snap(self):
        #TODO assume stream has started
        r, frame = self.vidstream.read()
        frame = cv2.flip(frame, 1)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        return frame

    def snaptk(self):
        frame = self.snap()
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        return imgtk


    def stream(self):
        while (True):
            frame = self.snap()
            cv2.imshow(self.windowname, frame)

            self.process(frame)

            # wait for quit
            key = cv2.waitKey(25)
            if key == ord('q'):
                self._clean()
                break

    def stop(self):
        self._clean()

    def _clean(self):
        if (self.capture is not None):
            self.capture.release()
        cv2.destroyAllWindows()
        self.vidstream = None

    def set_processf(self, func):
        self.process_func = func

    def process(self, frame):
        # open PIL image
        pil = Image.fromarray(frame).convert('L')
        res = self.scanner.scan(pil)

        if len(res) == 0:
            return

        if self.process_func is None:
            return


        key = res[0]['value']
        data = self.process_func(key)
        print data

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

    def scanframe(self, frame):
        pil = Image.fromarray(frame).convert('L')
        res = self.scan(pil)
        return res

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
                # print symbol.type, ": ", symbol.data
        return symbolreturns
