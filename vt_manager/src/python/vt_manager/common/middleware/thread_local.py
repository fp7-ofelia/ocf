
class threadlocal():
    stack = {}
    
thread_locals = threadlocal()

def push(key,value):
    thread_locals.stack[key] = value

def pull(key=None):

    if not key:
        return tread_locals.stack
    try:
	return thread_locals.stack[key]

    except:

	return None

