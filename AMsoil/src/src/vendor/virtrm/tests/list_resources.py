import subprocess

from subprocess import Popen, PIPE
Popen("wc -l xh-2.txt", shell=True, stdout=PIPE).communicate()[0]

def list_servers():
    command = "python /opt/gcf/src/omni.py -o -a https://localhost:8003 -V3 listresources"
    #output = subprocess.call(command, shell=False)
    #print output
    #subprocess.call(command.split())
    proc = subprocess.Popen(command.split(), stdout=subprocess.PIPE, shell=False)
    (out, err) = proc.communicate()
    #print out
    if not err:
        return True
    else:
        return False

print list_servers()
