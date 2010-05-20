'''
Created on May 19, 2010

@author: jnaous
'''

import paramiko

# based on example at http://stackoverflow.com/questions/760978/long-running-ssh-commands-in-python-paramiko-module-and-how-to-end-them
class SSHClientPlus(paramiko.SSHClient):
    @classmethod
    def exec_command_plus(cls, addr, username, password, cmd):
        client = cls()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(addr, username=username, password=password)
        transport = client.get_transport()
        client.channel = transport.open_session()
        client.channel.set_combine_stderr(True)
#        client.channel.setblocking(0)
#        client.std = client.channel.makefile("rw")
#        client.stderr = client.channel.makefile_stderr("r")
        client.channel.exec_command(cmd)
        return client
        
    def communicate(self, stdindata=None, check_closed=False):
        import socket
        if stdindata != None:
            if not check_closed:
                self.channel.sendall(stdindata)
            else:
                try:
                    self.channel.sendall(stdindata)
                except socket.error as e:
                    if "closed" not in "%s" % e:
                        raise
            
        out = ""
#        while True:
#            rl, wl, xl = select.select([self.channel], [], [], 0.0)
#            if len(rl) > 0:
#                out = out + self.channel.recv(1024)
#            else:
#                break
#        while True:
#            read = self.std.read(1024)
#            out = out + read
#            if len(read) < 1024:
#                break
        while self.channel.recv_ready():
            out = out + self.channel.recv(1024)
            
#        err = ""
#        while True:
#            read = self.stderr.read(1024)
#            out = out + read
#            if len(read) < 1024:
#                break
#        while self.channel.recv_stderr_ready:
#            err = err + self.channel.recv_stderr(1024)
#
#        return (out, err)
        return out

    def wait(self):
        status = self.channel.recv_exit_status()
        return status
