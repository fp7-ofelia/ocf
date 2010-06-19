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
    