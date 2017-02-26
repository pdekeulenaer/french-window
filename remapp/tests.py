import cv2
import scanner
from PIL import Image
import urllib2
import json

class Viewer:
    def __init__(self, windowname='Preview Window', feed=1):
        self.windowname = windowname
        self.feed = feed
        self.capture = None

        #initialize scanner
        self.scanner = scanner.Scanner()

        # set processing function
        self.process_func = None

    def start(self):
        stream = cv2.VideoCapture(self.feed)

        while (True):
            r, frame = stream.read()

            # show image
            cv2.imshow(self.windowname, frame)

            self.process(frame)

            # wait for quit
            key = cv2.waitKey(25)
            if key == ord('q'):
                self._clean()
                break

    def _clean(self):
        if (self.capture is not None):
            self.capture.release()
        cv2.destroyAllWindows()

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


class RemoteAccess:
    def __init__(self, host='localhost:8080'):
        self.host = host

    def fetch(self, key):
        query = 'http://%s/scan/ajax_bookdata/?key=%s' % (self.host, key)
        records = urllib2.urlopen(query).read()
        data = json.loads(records)
        return data

if __name__ == '__main__':
    v = Viewer()
    racc = RemoteAccess()

    v.set_processf(racc.fetch)
    v.start()

# if vc.isOpened(): # try to get the first frame
#     rval, frame = vc.read()
# else:
#     rval = False

# while rval:
#     cv2.imshow("preview", frame)
#     rval, frame = vc.read()
#     key = cv2.waitKey(20)
#     if key == 27: # exit on ESC
#         break

# cv2.destroyWindow("preview")
