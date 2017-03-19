import difflib
import urllib
import datetime
import base64

SIMILARITY_CUTOFF_DEFAULT = 0.6
# Calculates the ratio of similarity between 2 strings a and b
# Uses the 'Gestalt Pattern Matching' algorithm
# Returns a float number 0.0 < f < 1.0
def similarity(a,b):
    return difflib.SequenceMatcher(None, a,b).ratio()

# Returns True if strings a,b are sufficiently similar as defined by the Gestalt Pattern Matching ratio being above the specified cutoff
# Default cutoff value is 0.6
def issimilar(a,b,cutoff=SIMILARITY_CUTOFF_DEFAULT):
    return similarity(a,b) > cutoff

# Returns all matches that are sufficiently similar to a keyword
# Defaults to returning all matches above a cutoff of 0.6
# By specifying the n argument the number of possible matches can be reduced
def close_matches(keyword, possibilities, n=-1, cutoff=SIMILARITY_CUTOFF_DEFAULT):
    if n == -1: n = len(possibilities)
    return difflib.get_close_matches(keyword, possibilities, n=n, cutoff=cutoff)

# Returns the best possible match above a certain cutoff (default is 0.6)
# uses the Gestalt Pattern Matching algoirthm
def best_match(keyword, possibilities, cutoff=SIMILARITY_CUTOFF_DEFAULT):
    r = close_matches(keyword, possibilities, n=1, cutoff=cutoff)
    if len(r) > 0:
        return r[0]
    return None

def html_sanitize(s):
    if type(s) == str or type(s) == unicode:
        return s.replace("'","&#39;").replace('"',"&#34;")
    return s

def url_encode(s):
    return urllib.quote_plus(s)

def timestamp():
    return (datetime.datetime.now()).strftime('%Y%m%d_%H%M%S_%f')


class Image(object):
    snap_root = 'img/snapshots/'

    @classmethod
    def decode(cls, data, enc):
        decoded = None
        if enc == 'base64':
            decoded = base64.decodestring(data)
        else:
            return 'ERR - unknown encoding'

        return decoded


    @classmethod
    def snapstore(cls, name, data, enc, imgtype, stamp=True):
        fn = name
        if stamp:
            fn += '_' + timestamp()

        filename = '%s.%s' % (fn, imgtype.replace('image/','').replace('img/',''))
        f = open(cls.snap_root + filename, 'wb')

        decoded = cls.decode(data, enc)

        f.write(decoded)
        f.close()

        return 'Image saved'
