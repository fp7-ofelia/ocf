'''
@author jnaous
'''
try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()

def get_thread_locals():
    _thread_locals.d = getattr(_thread_locals, "d", {})
    return _thread_locals.d

class ParserRedefined(Exception):
    """
    Raised when L{models.ThreadLocals.add_parser} is called twice for the same
    keyword.
    """
    def __init__(self, keyword):
        self.keyword = keyword
        super(ParserRedefined, self).__init__(
            "Threadlocals parser to get keyword %s from request redefined." 
            % keyword)

class ThreadLocals(object):
    """Middleware that gets various objects from the
    request object and saves them in thread local storage."""
    
    __parsers = {}
    
    @classmethod
    def add_parser(cls, kw, func):
        """
        Add a function to parse a request, get an object, and store it in
        thread locals storage
        """
        if kw in cls.__parsers:
            raise ParserRedefined(kw)
        
        cls.__parsers[kw] = func

    def process_request(self, request):
        """Parse request and set keywords"""
        d = get_thread_locals()
        for kw, func in self.__parsers:
            d[kw] = func(request)
        
    def process_response(self, request, response):
        """Reset thread locals"""
        _thread_locals.d = {}
