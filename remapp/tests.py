import cv2
import scanner
from PIL import Image

class Viewer:
    def __init__(self, windowname='Preview Window', feed=1):
        self.windowname = windowname
        self.feed = feed
        self.capture = None

        #initialize scanner
        self.scanner = scanner.Scanner()

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

    def process(self, frame):
        # open PIL image
        pil = Image.fromarray(frame).convert('L')
        res = self.scanner.scan(pil)
        print res


if __name__ == '__main__':
    v = Viewer()
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
