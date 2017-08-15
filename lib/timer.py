import cProfile
import pstats
import StringIO

log = open('profile.log', 'wb')

def profile(func):
    def profiled_func(*args, **kwargs):
        profile = cProfile.Profile()
        try:
            profile.enable()
            result = func(*args, **kwargs)
            profile.disable()
            return result
        finally:
            s = StringIO.StringIO()
            ps = pstats.Stats(profile, stream=s).sort_stats('cumulative')
            ps.print_stats()
            print s.getvalue()

    return profiled_func
