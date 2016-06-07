from .compat import urlparse


def get_domain(url):
    return urlparse(url).hostname


def profileit(func):
    """
    Decorator (function wrapper) that profiles a single function
    @profileit()
    def func1(...)
            # do something
        pass
    """
    def wrapper(*args, **kwargs):
        import cProfile
        file_name = "/tmp/{}.pfl".format(func.__name__)
        prof = cProfile.Profile()
        retval = prof.runcall(func, *args, **kwargs)
        prof.dump_stats(file_name)
        return retval

    return wrapper
