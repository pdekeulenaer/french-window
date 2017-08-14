import ttk
import config
from Tkinter import *
from PIL import Image
from PIL import ImageTk
from imgproc import Viewer, Scanner
from client import Client

class Main(object):
    def __init__(self):
        self.root = Tk()
        self.initialize_main()
        self.root.title('French Window')
        self.root.protocol('WM_DELETE_WINDOW', self.destroy)

    def initialize_main(self):
        self.root.state('zoomed')
        self.menu()
        self.panes()

        self.videoPanel = ViewerPanel(self.left)
        self.tabs = Tabs(self.right)
        self.bottomBar = BottomBar(self.bottom)
        self.statusBar = StatusBar(self.status)

        self.videoPanel.top = self

        Logger.log('Loading completed')
        Logger.log('Ready for input')


    def destroy(self):
        self.videoPanel.top = None
        self.root.destroy()


    def initiateViewer(self):
        # initiatlizations
        self.viewer = Viewer()
        self.viewer.start()
        self.scanner = Scanner()
        scanner.register_callback('ISBN scanned', scanner.isbn_lookup)


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

        bottom = ttk.Labelframe(p, text='Status', width=1200, height=78)
        status = ttk.Frame(p, width=1200, height=25)

        p.add(bottom)
        p.add(status)

        self.left = left
        self.right = right
        self.bottom = bottom
        self.status = status

    def start(self):
        # Execute main loop
        self.root.mainloop()


class ViewerPanel(object):
    def __init__(self, root, top=None):
        self.root = root
        self.top = top
        self.initiateViewer()
        self.createScreen()
        self.scans = []

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

        self.videoFrame = videoFrame
        self.imglabel = imglabel

        self.update_frame()
        return None


    # callback definitions
    def update_frame(self):
        frame = self.viewer.snap()

        # scanning barcode
        ret = self.scanner.scanframe(frame)
        if len(ret) > 0:
            if self.top is not None:
                self.top.statusBar.setStatus('ISBN: ' + ret[0]['value'])
            self.scan(ret[0]['value'])  #TODO - hceck this with camera
        else:
            if self.top is not None:
                self.top.statusBar.clear()

        # printing to screen
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.imglabel.imgtk = imgtk
        self.imglabel.configure(image=imgtk)
        self.imglabel.after(10, self.update_frame)

    def close(self):
        self.viewer.stop()
        self.root.destroy()

    def scan(self, isbn):
        if isbn in self.scans:
            print "%s already scanned" % isbn
            return #if this book is already scanned, do nothing

        self.scans.append(isbn)
        # open client connection
        Logger.log("Loading ISBN code: %s" % isbn)
        c = Client(config.user, config.password)       # TODO - secure it
        bookdata = c.isbn_lookup(isbn)

        if self.top is not None:
            if 'error' in bookdata.keys():
                self.top.tabs.addTab('Unknown book', {})
            else:
                self.top.tabs.addTab(bookdata['book']['title'],bookdata['book'])
        else:
            print "ERR - top level not defined"

        return

    # def force(self):
    #     isbn = '9780817405021'
    #     self.scan(isbn)

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
        print self.data
        if 'author' in self.data.keys() and self.data['author'] is not None:
            print self.data['author']
            authorname = self.data['author'].setdefault('name','')

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
        series_nr_iv = IntVar()

        series_name = Entry(bookform, textvariable=series_name_sv).grid(column=1, row=len(self.stringvars)+4, sticky=W+E)

        ttk.Label(bookform, text="Series nr").grid(column=0, row=len(self.stringvars)+5, sticky=W)
        series_nr = Entry(bookform, textvariable=series_nr_iv).grid(column=1, row=len(self.stringvars)+5, sticky=W+E)
        self.series_nr = series_nr_iv
        self.stringvars['Series'] = series_name_sv

        # Add 'submit' button
        closeButton = ttk.Button(bookform, text="close", command=self.close).grid(row=len(self.stringvars)+6, column=0)
        submitButton = ttk.Button(bookform, text="Submit", command=self.submit).grid(row=len(self.stringvars)+6, column=1)

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
        self.data['is_series'] = (self.is_series.get() == 1)
        self.data['series_nr'] = self.series_nr.get()
        self.data['series_name'] = self.stringvars['Series'].get()

class BottomBar(object):
    def __init__(self, root):
        self.root = root
        self.create()
        Logger._logger_outputs.append(self)

    def create(self):
        frame = ttk.Frame(self.root)
        frame.pack(expand=True, fill=BOTH)

        scrollbar = Scrollbar(self.root)
        scrollbar.pack(side=RIGHT, fill=BOTH)

        loggerbox = Text(self.root, state='disabled', yscrollcommand=scrollbar.set)
        loggerbox.pack(expand=True, fill=BOTH)

        self.logger = loggerbox
        self.counter = 1

    def log(self, msg, code=None):
        if code is not None:
            c = '[%s] ' % code
        else:
            c = ''

        print self.counter

        self.logger.config(state='normal')
        self.logger.insert(END, '%s%s\n' % (c, msg))
        self.logger.see(END)
        self.logger.config(state='disabled')
        self.counter += 1

class Logger(object):
    _logger_outputs = []

    @classmethod
    def log(cls, msg):
        for lo in cls._logger_outputs:
            lo.log(msg)

if __name__ == '__main__':
    gui = Main()
    gui.start()
