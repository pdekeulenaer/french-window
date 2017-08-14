import Queue

logger = None

def logger():
    global logger
    if logger is None:
        logger = Logger()
    return logger


class Logger():
    def __init__(self):
        self.q = Queue()

    def log(self, msg, code=0):
        pass

    def _addToQueue(self, msg):
        pass

    def pop(self, msg):

