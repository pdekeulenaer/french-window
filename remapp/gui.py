from Tkinter import *
from PIL import Image
from PIL import ImageTk
import ttk

from tests import Viewer
from scanner import Scanner

# initiatlizations
viewer = Viewer()
viewer.start()

scanner = Scanner()

def maingui():
    # callback definitions
    def update_frame():
        frame = viewer.snap()

        # scanning barcode
        ret = scanner.scanframe(frame)
        if len(ret) > 0:
            isbnVar.set('ISBN: ' + ret[0]['value'])
            print ret

        # printing to screen
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        imglabel.imgtk = imgtk
        imglabel.configure(image=imgtk)
        imglabel.after(10, update_frame)

        # print ret


    def close():
        viewer.stop()
        root.destroy()

    root = Tk()
    root.title("Videostream window")

    # creating the screens

    videoFrame = ttk.Frame(root, width=600, height=500, padding="5 5 5 5")
    videoFrame.grid(column=0,row=0, sticky=(N,W,E,S))

    imglabel = ttk.Label(videoFrame)
    imglabel.grid(row=0, column=0)


    mainframe = ttk.Frame(root, width=600, height=100, padding="3 3 12 12")
    mainframe.grid(column=0,row=600,sticky=(N,W,E,S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weigh=1)

    isbnVar = StringVar()
    isbnVar.set("No ISBN code detected")

    # isbnlabel = ttk.Label(mainframe, text="ISBN:").grid(column=0,row=0,sticky=(N,W))
    isbncontent = ttk.Label(mainframe, textvariable=isbnVar).grid(column=0, row=0, sticky=(N,W))
    ttk.Button(mainframe, text="Close", command=close).grid(column=2, row=10, sticky=E)

    update_frame()
    root.mainloop()

def bookgui():
    form = Tk()
    form.title("Set book details")

    bookform = ttk.Frame(form, width=400,heigh=500, padding="5 5 5 5")
    bookform.columnconfigure(0, minsize=100)
    bookform.columnconfigure(1, minsize=300)
    bookform.grid(column=0,row=0,sticky=(N,W,E,S))


    stringvars = {}
    def generate(var, label=None, widget=ttk.Entry):
        counter = len(stringvars)

        if label is None:
            label = var
        ttk.Label(bookform, text=label).grid(column=0, row=counter, sticky=W)
        entryvar = StringVar()
        widget(bookform, textvariable=entryvar).grid(column=1, row=counter, sticky=W+E)

        stringvars[var] = entryvar


    #row 1
    # titleLabel = ttk.Label(bookform, text="Title").grid(column=0, row=0, sticky=W)
    # titleEntryVar = StringVar()
    # titleEntry = ttk.Entry(bookform, textvariable=titleEntryVar).grid(column=1, row=0, sticky=W+E)
    generate("Title")
    generate("Author")
    generate("Language")
    generate("Publisher")
    generate("Publish date")
    generate("ISBN10")
    generate("ISBN13")

    ttk.Label(bookform, text="Summary").grid(column=0, row=len(stringvars), sticky=W)
    textvar = Text(bookform, height=5, width=10).grid(column=1,row=len(stringvars), sticky=W+E)
    stringvars['Summary'] = textvar

    # Add 'submit' button

    submitButton = ttk.Button(bookform, text="Submit").grid(row=len(stringvars), column=0, columnspan=2)

    for child in bookform.winfo_children(): child.grid_configure(padx=5, pady=5)

    form.mainloop()


bookgui()

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

