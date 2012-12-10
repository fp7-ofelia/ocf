'''
@author: jnaous
'''
try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

from threading import current_thread, Lock
import os

'''
Management of the permissions dictionary, depending
on the current thread and its containing process.
'''

# Returns key (processPID_threadID) for permissions dictionary
def get_tpid_key():
    return str(os.getpid())+"_"+str(current_thread().ident)

class threadlocal(local):
    d_stack = {}
    
_thread_locals = threadlocal()

def push_frame(**kw):
    """
    Push a new frame on the dictionary.
    """
    _thread_locals.d_stack[get_tpid_key()]=kw

def pop_frame():
    """
    Pop a specific frame from the dictionary.
    """
    try:
        _thread_locals.d_stack.pop(get_tpid_key())
    except KeyError:
        print "[WARNING] Exception at 'expedient.common.middleware.threadlocals.ThreadLocals': tried to access to permittees stack when it was already empty. This may happen because an incorrect URL (request.url) was requested and Django's CommonMiddleware forwarded it to a new one without processing the request in this middleware."
        pass

def get_thread_locals():
    """
    Returns the dictionary of all parsed keywords in the request.
    """
    return _thread_locals.d_stack[get_tpid_key()]

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
#    ThreadLocals.add_parser(kw, func)
    pass

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

    def __init__(self):
        from expedient.clearinghouse.permissionmgmt.models import get_project, get_slice, get_user
        self.__parsers = {}
        self.add_parser("user", get_user)
        self.add_parser("project", get_project)
        self.add_parser("slice", get_slice)

#    @classmethod
    def add_parser(self, kw, func):
        """
        Add a function to parse a request, get an object, and store it in
        thread locals storage
        """
        if kw in self.__parsers:
            raise ParserRedefined(kw)
        
        self.__parsers[kw] = func

    def process_request(self, request):
        """Parse request and set keywords"""
        try:
            d = {}
            for kw, func in self.__parsers.items():
                d[kw] = func(request)
            push_frame(**d)
        except Exception as e:
            print "[WARNING] Exception at 'expedient.common.middleware.threadlocals.ThreadLocals': tried to execute unknown function: %s" % str(e)
        return None
        
    def process_response(self, request, response):
        """Reset thread locals"""
        pop_frame()
        return response
