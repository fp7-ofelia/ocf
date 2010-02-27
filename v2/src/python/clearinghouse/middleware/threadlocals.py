# threadlocals middleware
from clearinghouse.security.models import connect_all_signals,\
    disconnect_all_signals

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()
def get_current_user():
    return getattr(_thread_locals, 'user_stack', [None])[-1]

def push_current_user(u):
    _thread_locals.user_stack = getattr(_thread_locals, 'user_stack', [])
    _thread_locals.user_stack.append(u)

def pop_current_user(u):
    _thread_locals.user_stack = getattr(_thread_locals, 'user_stack', [None, None])
    return _thread_locals.user_stack.pop()

def push_admin_mode():
    _thread_locals.admin_stack = getattr(_thread_locals, 'admin_stack', [])
    if not _thread_locals.admin_stack:
        # disconnect all signals
        disconnect_all_signals()
    _thread_locals.admin_stack.append(True)
    
def pop_admin_mode():
    _thread_locals.admin_stack = getattr(_thread_locals, 'admin_stack', [])
    if not _thread_locals.admin_stack:
        raise AdminModeException()
    connect_all_signals()
    _thread_locals.admin_stack.pop()

class AdminModeException(Exception):
    '''Should be raised when pop_admin_mode is called but not 
    already in admin mode'''

class ThreadLocals(object):
    """Middleware that gets various objects from the
    request object and saves them in thread local storage."""
    def process_request(self, request):
        _thread_locals.user_stack = [getattr(request, 'user', None)]
