import events
import screens
import client
import config


def launchGUI():
    gui = screens.Main()
    gui.start()
    return gui

def loadClient():
    c = client.Client(config.user, config.password)
    return c

c = loadClient()
gui = launchGUI()

