'''
@author jnaous
'''
try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

class threadlocal(local):
    d_stack = []
    
_thread_locals = threadlocal()

def push_frame(**kw):
    """
    Push a new frame on the stack.
    """
    _thread_locals.d_stack.append(kw)

def pop_frame():
    """
    Pop a frame from the stack.
    """
    try:
        _thread_locals.d_stack.pop()
    except IndexError:
        pass

def get_thread_locals():
    """
    Returns the dictionary of all parsed keywords in the request.
    """
    return _thread_locals.d_stack[-1]

def add_parser(kw, func):
    """
    Add a request parser for a keyword.
    When a request arrives, the parser C{func} will be used to set the value
    for the C{kw} keyword in the thread-local storage.
    
    @param kw: The keyword to use for the result of this parser.
    @type kw: hashable value
    @param func: a function that accepts the request and returns a value
    @type func: callable.
    """
    ThreadLocals.add_parser(kw, func)

def get_parser(kw):
    """
    Get the parser function stored for the keyword C{kw} or None if
    it doesn't exist.
    """
    return ThreadLocals.__parser.get(kw, None)

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
        d = {}
        for kw, func in self.__parsers.items():
            d[kw] = func(request)
        push_frame(**d)    
        return None
        
    def process_response(self, request, response):
        """Reset thread locals"""
        pop_frame()
        return response
    