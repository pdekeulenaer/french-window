import lib
import web

# configuration settings
DEBUG = True

# database settings
lib.db.DB_TYPE = 'sqlite'
lib.db.DBNAME = 'data/french_window.db'
lib.db.DBNAME_TEST = 'data/test_french_window.db'


# Session setting
# web.config.debug = False
web.config.session_parameters['cookie_name'] = 'french_window_session_id'
web.config.session_parameters['timeout'] = 86400*30
web.config.session_parameters['ignore_expiry'] = True



# COnfiguration logic
if DEBUG:
    lib.db.DBNAME = lib.db.DBNAME_TEST
