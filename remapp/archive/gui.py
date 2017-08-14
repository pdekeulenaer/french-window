from Tkinter import *
from PIL import Image
from PIL import ImageTk
import ttk

from tests import Viewer
from scanner import Scanner
from client import Client

class BookScreen(object):
    def __init__(self, root, bookdata={}):
        self.form = Toplevel(root)
        self.stringvars = {}
        self.data = bookdata
        print "----------------------"
        print "creating bookscreen with lots of data"
        print self.data
        self.createForm(self.form)

    def createForm(self, form):
        form.title("Set book details")

        bookform = ttk.Frame(form, width=400,heigh=500, padding="5 5 5 5")
        bookform.columnconfigure(0, minsize=100)
        bookform.columnconfigure(1, minsize=300)
        bookform.grid(column=0,row=0,sticky=(N,W,E,S))

        def generate(var, val="", label=None, widget=ttk.Entry):
            counter = len(self.stringvars)

            if label is None: label = var

            ttk.Label(bookform, text=label).grid(column=0, row=counter, sticky=W)
            sv = StringVar()
            sv.set(val)
            # FIX padding on this
            ev = Entry(bookform, textvariable=sv).grid(column=1, row=counter, sticky=W+E)
            # widget(bookform, textvariable=entryvar)

            self.stringvars[var] = sv


        generate("Title", self.data['title'])
        generate("Author", self.data['author']['name'])
        generate("Language", self.data['language'])
        generate("Publisher", self.data['publisher'])
        generate("Publish date", self.data["publish_date"])
        generate("ISBN10", self.data["isbn10"])
        generate("ISBN13", self.data["isbn13"])

        ttk.Label(bookform, text="Summary").grid(column=0, row=len(self.stringvars), sticky=W)
        sv = StringVar()
        sv.set(self.data['summary'])
        textvar = Text(bookform, height=5, width=10).grid(column=1,row=len(self.stringvars), sticky=W+E)
        # FIX TEXT SETTING OF THIS
        self.stringvars['Summary'] = textvar

        # Add 'submit' button

        submitButton = ttk.Button(bookform, text="Submit").grid(row=len(self.stringvars), column=0, columnspan=2)
        for child in bookform.winfo_children(): child.grid_configure(padx=5, pady=5)

    def close(self):
        self.form.destroy()

    def submit(self):
        # Temp hack to test E2E flow
        c = Client('meg','1234')
        print 'SUBMITTING BOOK'
        resp = c.add_book(self.data)
        pp.pprint(resp)

class MainScreen(object):
    def __init__(self):
        self.initiateViewer()
        self.root = Tk()
        # self.root.state('zoomed')

    def initiateViewer(self):
        # initiatlizations
        self.viewer = Viewer()
        self.viewer.start()
        self.scanner = Scanner()


    def createScreen(self):
        self.root.title("Videostream window")

        # creating the screens
        videoFrame = ttk.Frame(self.root, width=600, height=500, padding="5 5 5 5")
        videoFrame.grid(column=0,row=0, sticky=(N,W,E,S))

        imglabel = ttk.Label(videoFrame)
        imglabel.grid(row=0, column=0)

        mainframe = ttk.Frame(self.root, width=600, height=100, padding="3 3 12 12")
        mainframe.grid(column=0,row=600,sticky=(N,W,E,S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weigh=1)

        isbnVar = StringVar()
        isbnVar.set("No ISBN code detected")

        # isbnlabel = ttk.Label(mainframe, text="ISBN:").grid(column=0,row=0,sticky=(N,W))
        isbncontent = ttk.Label(mainframe, textvariable=isbnVar).grid(column=0, row=0, sticky=(N,W))
        ttk.Button(mainframe, text="Close", command=self.close).grid(column=2, row=10, sticky=E)
        ttk.Button(mainframe, text="Force", command=self.force).grid(column=1, row=10, sticky=E)

        self.videoFrame = videoFrame
        self.imglabel = imglabel
        self.mainframe = mainframe
        self.isbnVar = isbnVar
        self.isbncontent = isbncontent

        return (videoFrame, imglabel, mainframe, isbnVar, isbncontent)

    def start(self):
        (vf, il, mf, iv, isbn) = self.createScreen()
        # Register the callbacks
        self.update_frame()

        # Execute main loop
        self.root.mainloop()

    # callback definitions
    def update_frame(self):
        frame = self.viewer.snap()

        # scanning barcode
        ret = self.scanner.scanframe(frame)
        if len(ret) > 0:
            self.isbnVar.set('ISBN: ' + ret[0]['value'])
            print ret

        # printing to screen
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.imglabel.imgtk = imgtk
        self.imglabel.configure(image=imgtk)
        self.imglabel.after(10, self.update_frame)
        # print ret


    def close(self):
        self.viewer.stop()
        self.root.destroy()

    def force(self):
        isbn = '9780817405021'
        # Temp hack to test E2E flow
        c = Client('meg','1234')
        bookdata = c.isbn_lookup(isbn)
        # resp = c.test_auth()
        print type(bookdata)
        book = BookScreen(self.root, bookdata['book'])


if __name__ == '__main__':
    gui = MainScreen()
    gui.start()

# feet = StringVar()
# meters = StringVar()

# feet_entry = ttk.Entry(mainframe, width=7, textvariable=feet)
# feet_entry.grid(column=2, row=1, sticky=(W,E))

# ttk.Label(mainframe, textvariable=meters).grid(column=2, row=2, sticky=(W,E))

# ttk.Label(mainframe, text="feet").grid(column=3, row=1, sticky=W)
# ttk.Label(mainframe, text="is equivalent to").grid(column=1, row=2, sticky=E)
# ttk.Label(mainframe, text="meters").grid(column=3, row=2, sticky=W)

# for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

# feet_entry.focus()

# root.bind('<Return>', calculate)

