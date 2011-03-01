'''
Created on Jun 16, 2010

@author: jnaous
'''

import logging
from urlparse import urlunparse, urlparse
logger = logging.getLogger("test_utils")

def test_to_http(url):
    """return a url with "test" scheme replaced by "http".
    
    @param url: the url to edit
    @return: A url string
    """
    l = list(urlparse(url))
    if l[0].lower() == "test":
        l[0] = "http"
    return urlunparse(l)

def run_cmd_in_xterm(cmd, pause=False):
    """
    Runs a command in a subprocess xterm.
    """
    if pause:
        cmd = cmd + "; read n"
    cmd = "xterm -e '%s'" % cmd
    
    return _run_cmd(cmd)

def run_cmd(cmd, pause=False):
    return _run_cmd("sh -c '%s'" % cmd, pause)

def _run_cmd(cmd, pause=False):
    import shlex, subprocess
    if pause:
        cmd = cmd + "; read n"
    return subprocess.Popen(
	shlex.split(cmd),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    
def drop_to_shell(local):
    import rlcompleter
    import readline
    import code
    readline.parse_and_bind("tab: complete")
    code.interact(local=local)

def wait_for_servers(urls, timeout):
    import time, urlparse, httplib
    from ssl import SSLError
    
    for u in urls:
        parsed = urlparse.urlparse(u.lower(), "https")
        netloc = parsed.hostname
        if parsed.port: netloc = "%s:%s" % (netloc, parsed.port)
        if parsed.scheme == "http":
            cnxn = httplib.HTTPConnection(netloc)
        elif parsed.scheme == "https":
            cnxn = httplib.HTTPSConnection(netloc)
        else:
            raise Exception("Don't know how to handle scheme %s" % parsed.scheme)
        i = 0
        while(i < timeout):
            try:
                cnxn.connect()
            except SSLError:
                break;
            except Exception as e:
                if "Connection refused" in str(e):
                    time.sleep(1)
                    i = i - 1
                elif "SSL" in str(e):
                    break
                else:
                    raise
            else:
                break
            
def wrap_xmlrpc_call(func, args, kwargs, timeout):
    '''
    Keep trying the xmlrpc call until a timeout occurs on errors that are not
    xmlrpclib Faults.
    
    @param func: the function to call
    @param args: list of arguments to pass to call
    @param kwargs: dict of keyword args to pass to func
    @param timeout: How many seconds to keep trying for.
    '''
    import time, xmlrpclib
    for i in xrange(timeout):
        try:
            r = func(*args, **kwargs)
            return r
        except xmlrpclib.Fault:
            raise
        except:
            logger.debug("     Trying to call func for the {%s}th again." % (i+1,))
            time.sleep(1)
            pass
    return func(*args, **kwargs)
