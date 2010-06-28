'''
Created on Jun 16, 2010

@author: jnaous
'''

def run_cmd_in_xterm(cmd, pause=False):
    """
    Runs a command in a subprocess xterm.
    """
    if pause:
        cmd = cmd + "; read n"
    cmd = "xterm -e '%s'" % cmd
    
    return run_cmd(cmd)

def run_cmd(cmd, pause=False):
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
            
