import ttk
from Tkinter import *
from PIL import Image
from PIL import ImageTk
from imgproc import Viewer, Scanner
from client import Client

class BookScreen(object):
    def __init__(self, root, tabs, bookdata={}):
        self.stringvars = {}
        self.data = bookdata
        self.root = root
        self.tabs = tabs
        self.createForm(self.root)


    # TODO - add "is series" checkbox
    # TODO - abstract to book objects - currently quite messy
    # TODO - open web interface if needed
    def createForm(self, form):
        bookform = ttk.Frame(form, width=550,heigh=800, padding="5 5 5 5")
        bookform.columnconfigure(0, minsize=100)
        bookform.columnconfigure(1, minsize=450)
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


        # Author name
        authorname = ''
        if 'author' in self.data.keys():
            authorname = self.data['author']['name']

        generate("Title", self.data.setdefault('title',''))
        generate("Author", authorname)
        generate("Language", self.data.setdefault('language',''))
        generate("Publisher", self.data.setdefault('publisher',''))
        generate("Publish date", self.data.setdefault("publish_date",''))
        generate("ISBN10", self.data.setdefault("isbn10",''))
        generate("ISBN13", self.data.setdefault("isbn13",''))

        ttk.Label(bookform, text="Summary").grid(column=0, row=len(self.stringvars), sticky=W)

        # Scrollbar summary
        summaryframe = ttk.Frame(bookform)
        summaryframe.grid(column=1, row=len(self.stringvars), sticky=W+E)

        scrollbar = Scrollbar(summaryframe)
        scrollbar.pack(side=RIGHT, fill=BOTH)

        textvar = Text(summaryframe, height=5, width=10, yscrollcommand=scrollbar.set)
        textvar.pack(expand=True, fill=X)
        textvar.insert('1.0', self.data.setdefault('summary',''))
        self.summaryvar = textvar
        scrollbar.config(command=textvar.yview)
        self.stringvars['Summary'] = self.summaryvar

        # Create the "is_series" checkmark and series name
        series_var = IntVar()
        series = Checkbutton(bookform, text="Part of series", variable=series_var).grid(column=0, row=len(self.stringvars)+4, sticky=W)
        self.is_series = series_var

        series_name_sv = StringVar()
        series_name = Entry(bookform, textvariable=series_name_sv).grid(column=1, row=len(self.stringvars)+4, sticky=W+E)
        self.stringvars['Series'] = series_name_sv

        # Add 'submit' button
        closeButton = ttk.Button(bookform, text="close", command=self.close).grid(row=len(self.stringvars)+5, column=0)
        submitButton = ttk.Button(bookform, text="Submit", command=self.submit).grid(row=len(self.stringvars)+5, column=1)

        for child in bookform.winfo_children(): child.grid_configure(padx=5, pady=5)

    def close(self):
        self.tabs.removeTab(self)

    def submit(self):
        # Temp hack to test E2E flow
        self.refresh()
        c = Client('meg','1234')
        resp = c.add_book(self.data)
        print(resp)
        self.close()

    def refresh(self):
        if 'author' not in self.data.keys() or self.data['author'] is None:
            print 'ERR - no author'
            self.data['author'] = {}
            self.data['author']['id'] = -1

        self.data['author']['name'] = self.stringvars['Author'].get()
        self.data['title'] = self.stringvars['Title'].get()
        self.data['langauge'] = self.stringvars['Language'].get()
        self.data['publisher'] = self.stringvars['Publisher'].get()
        self.data['publish_date'] = self.stringvars['Publish date'].get()
        self.data['isbn10'] = self.stringvars['ISBN10'].get()
        self.data['isbn13'] = self.stringvars['ISBN13'].get()
        self.data['summary'] = self.summaryvar.get('1.0', 'end-1c') # reads from 1st char, 0th line, until last char - 1, to avoid newline
        self.data['is_series'] = self.is_series == 1
        self.data['series_name'] = self.stringvars['Series'].get()


class Tabs(object):
    def __init__(self, root):
        self.root = root
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill=BOTH, padx=5, pady=3)
        self.tabs = {}

    def addTab(self, name, data={}):
        page = ttk.Frame(self.nb)
        self.nb.add(page, text=name)
        book = BookScreen(page, self, data)
        self.tabs[book] = page

    def removeTab(self, bookscreen):
        self.nb.forget(self.tabs[bookscreen])

class Main(object):
    def __init__(self):
        self.root = Tk()
        self.initialize_main()
        self.root.title('French Window')

    def initialize_main(self):
        self.root.state('zoomed')
        self.menu()
        self.panes()

        videoPanel = ViewerPanel(self.left)
        # bookPanel = BookScreen(self.right)
        tabs = Tabs(self.right)
        bottomBar = BottomBar(self.bottom, tabs)
        statusBar = StatusBar(self.root)
        # self.videoScreen(self.left)

    def initiateViewer(self):
        # initiatlizations
        self.viewer = Viewer()
        self.viewer.start()
        self.scanner = Scanner()


    def menu(self):
        menubar = Menu(self.root)
        menubar.add_command(label='File', command='file')
        menubar.add_command(label='Config', command='config')
        menubar.add_command(label='Close', command=self.root.quit)
        self.root.config(menu=menubar)
        def file():
            pass

        def config():
            pass

    def panes(self):
        p = ttk.Panedwindow(self.root)
        p.pack(fill=BOTH, expand=1)
        p_top = ttk.Panedwindow(p, orient=HORIZONTAL)
        p.add(p_top)

        left = ttk.Labelframe(p_top, text='Video Capture', width=1200, height=600)
        right = ttk.Labelframe(p_top, text='Book submission', width=400, height=600)

        p_top.add(left)
        p_top.add(right)

        bottom = ttk.Labelframe(p, text='Status', width=1200, height=100)
        p.add(bottom)

        self.left = left
        self.right = right
        self.bottom = bottom

    def start(self):
        # Execute main loop
        self.root.mainloop()


class ViewerPanel(object):
    def __init__(self, root):
        self.root = root
        self.initiateViewer()
        self.createScreen()

    def initiateViewer(self):
        # initiatlizations
        self.viewer = Viewer()
        self.viewer.start(1024,600)
        self.scanner = Scanner()

    def createScreen(self):
        # creating the screens
        videoFrame = ttk.Frame(self.root, width=1200, height=600, padding="5 5 5 5")
        videoFrame.grid(column=0,row=0, sticky=(N,W,E,S))

        imglabel = ttk.Label(videoFrame)
        imglabel.grid(row=0, column=0)

        # mainframe = ttk.Frame(self.root, width=1200, height=600, padding="3 3 12 12")
        # mainframe.grid(column=0,row=600,sticky=(N,W,E,S))
        # mainframe.columnconfigure(0, weight=1)
        # mainframe.rowconfigure(0, weigh=1)

        # isbnVar = StringVar()
        # isbnVar.set("No ISBN code detected")

        # # isbnlabel = ttk.Label(mainframe, text="ISBN:").grid(column=0,row=0,sticky=(N,W))
        # isbncontent = ttk.Label(mainframe, textvariable=isbnVar).grid(column=0, row=0, sticky=(N,W))
        # ttk.Button(mainframe, text="Close", command=self.close).grid(column=2, row=10, sticky=E)
        # ttk.Button(mainframe, text="Force", command=self.force).grid(column=1, row=10, sticky=E)

        self.videoFrame = videoFrame
        self.imglabel = imglabel

        # self.mainframe = mainframe
        # self.isbnVar = isbnVar
        # self.isbncontent = isbncontent

        self.update_frame()
        return None


    # callback definitions
    def update_frame(self):
        frame = self.viewer.snap()

        # scanning barcode
        ret = self.scanner.scanframe(frame)
        if len(ret) > 0:
            self.isbnVar.set('ISBN: ' + ret[0]['value'])
            self.scan(ret[0]['value'])  #TODO - hceck this with camera

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

    def scan(self, isbn):
        if isbn in self.scans: return #if this book is already scanned, do nothing

        # open client connection
        c = Client('meg', '1234')       # TODO - put this in config and secure it
        bookdata = c.isbn_lookup(isbn)
        book = BookScreen(self.root, bookdata['book'])

    def force(self):
        isbn = '9780817405021'
        self.scan(isbn)

class BottomBar(object):
    def __init__(self, root, tabs):
        self.root = root
        self.tabs = tabs
        self.frame = ttk.Frame(self.root)
        self.frame.grid(column=0, row=0, sticky=(N,W,E,S))
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.create()

    def create(self):
        forceButton = ttk.Button(self.frame, text="Force", command=self.force).grid(column=0, row=0, sticky=W)

    def force(self):
        isbn = 'xxx9xxx780817405021'
        # Temp hack to test E2E flow
        c = Client('meg','1234')
        bookdata = c.isbn_lookup(isbn)
        # resp = c.test_auth()

        if 'error' in bookdata.keys():
            print "ERR - book not found"
            self.tabs.addTab("New book", {})
            return

        self.tabs.addTab(bookdata['book']['title'], bookdata['book'])




class StatusBar(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.variable = StringVar()
        self.label = Label(self, bd=1, relief=SUNKEN, anchor=W,
                           textvariable=self.variable,
                           font=('arial',10,'normal'), padx="5")
        self.variable.set('[Status bar to be set]')
        self.label.pack(fill=X, expand=True)
        self.pack(fill=X, expand=True, anchor=S)

    def setStatus(self, var):
        self.variable.set(var)

    def clear(self):
        self.variable.set('')

if __name__ == '__main__':
    gui = Main()
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

