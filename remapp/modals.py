from Tkinter import *
import ttk
import config

class ConfigWindow(object):
    def __init__(self, root):
        self.root = root
        self.window = Toplevel(self.root)
        self.window.title('Configuration')
        self.window.geometry('300x150')

        self.create(self.window)

    def create(self, master):
        Grid.columnconfigure(master, 1, weight=3)
        Grid.columnconfigure(master, 0, weight=1)
        Grid.rowconfigure(master, 3, weight=1)

        Label(master, text="Username").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        Label(master, text="Password").grid(row=1, column=0, sticky=W, padx=5, pady=5)
        Label(master, text="URL").grid(row=2, column=0, sticky=W, pady=5, padx=5)

        self.user = StringVar()
        self.pw = StringVar()
        self.url = StringVar()

        self.loadConfig()

        Entry(master, textvariable=self.user).grid(row=0, column=1, sticky=(W,E), padx=5, pady=5)
        Entry(master, textvariable=self.pw, show='*').grid(row=1, column=1,sticky=(W,E), padx=5, pady=5)
        Entry(master, textvariable=self.url).grid(row=2, column=1,sticky=(W,E), padx=5, pady=5)

        submitButton = ttk.Button(master, text="Update", command=self.submit).grid(row=3, column=0, columnspan=2)

    def submit(self):
        config.user = self.user.get()
        config.password = self.pw.get()
        config.api_hook = self.url.get()
        config.store()

        self.window.destroy()

    def loadConfig(self):
        self.user.set(config.user)
        self.pw.set(config.password)
        self.url.set(config.api_hook)


if __name__ == '__main__':
    root = Tk()
    w = ConfigWindow(root)

    root.mainloop()

