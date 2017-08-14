

class Event(object):
    def __init__(self, name, data, autofire=True):
        self.name = name
        self.data = data
        self.results = []
        if autofire:
            self.fire()

    def fire(self):
        for obs in Observer._observers:
            if self.name in obs._callbacks.keys():
                res = obs._callbacks[self.name](self.data)
                if res is not None:
                    self.results.append(res)

class Observer(object):
    _observers = []

    def __init__(self):
        self._observers.append(self)
        self._callbacks = {}

    def register_callback(self, event_name, callback):
        self._callbacks[event_name] = callback


class ScanEvent(Event):
    def __init__(self, code):
        super(ScanEvent, self).__init__('ISBN scanned', code)

class LogEvent(Event):
    def __init__(self, code, msg):
        super(LogEvent, self).__init__('LOG', msg)

class ScanObserver(Observer):
    def __init__(self):
        super(ScanObserver, self).__init__()

    def hit(self, code):
        print "A code was scanned %s" % (code)

scanner = ScanObserver()
scanner.register_callback('ISBN scanned', scanner.hit)
