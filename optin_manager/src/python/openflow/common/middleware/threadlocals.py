'''
@author jnaous
'''
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

def pop_current_user():
    _thread_locals.user_stack = getattr(_thread_locals, 'user_stack',
                                        [None, None])
    return _thread_locals.user_stack.pop()

def push_obj(obj):
    _thread_locals.obj_stack = getattr(_thread_locals, 'obj_stack', [])
    _thread_locals.obj_stack.append(obj)
    
def pop_obj():
    _thread_locals.obj_stack = getattr(_thread_locals, 'obj_stack', [])
    if not _thread_locals.obj_stack:
        raise ObjStackException()
    return _thread_locals.obj_stack.pop()

class ObjStackException(Exception):
    '''Should be raised when pop_obj is called but there's 
    nothing on the stack''' 
    pass

class ThreadLocals(object):
    """Middleware that gets various objects from the
    request object and saves them in thread local storage."""
    def process_request(self, request):
        _thread_locals.user_stack = [getattr(request, 'user', None)]
        
    def process_response(self, request, response):
        pop_current_user()
    