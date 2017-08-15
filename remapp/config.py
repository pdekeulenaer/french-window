import ConfigParser

# Static values
debug = True
cfg_file = 'config.cfg'


def loadConfig(fname):
    config = ConfigParser.RawConfigParser()
    config.read(fname)
    return config

def store(fname=None):
    if fname is None:
        fname = cfg_file

    config.set('Connection', 'url', api_hook)
    config.set('User Details', 'user', user)
    config.set('User Details', 'password', password)

    f = open(fname, 'wb')
    config.write(f)
    f.close()

config = loadConfig(cfg_file)

# Values to use in rest of app
api_hook = config.get('Connection','url')
user = config.get('User Details', 'user')
password = config.get('User Details', 'password')
