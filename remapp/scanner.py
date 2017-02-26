from PIL import Image
import zbar, io

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
