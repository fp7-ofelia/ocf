'''
Created on May 19, 2010

Has a class that is useful for sending commands to remote ssh servers and
interacting with them easily.

@author: jnaous
'''

import paramiko, logging
plogger = paramiko.util.get_logger("paramiko.transport")
plogger.setLevel(logging.WARNING)

logger = logging.getLogger("SSHClientPlus")

class TimeoutException(Exception):
    pass

class SSHClientPlus(paramiko.SSHClient):
    @classmethod
    def exec_command_plus(cls, addr, username, password, cmd, port=22):
        client = cls()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(addr, username=username, password=password, port=port)
        transport = client.get_transport()
        client.channel = transport.open_session()
        client.channel.set_combine_stderr(True)
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
        while self.channel.recv_ready():
            out = out + self.channel.recv(1024)
            
        return out

    def wait(self):
        status = self.channel.recv_exit_status()
        return status

    def wait_for_prompt(self, prompt="> ", timeout=10):
        import time
        read = ""
        while timeout:
            out = self.communicate()
            read += out
            
            if out.endswith(prompt):
                return read

            time.sleep(1)
            timeout = timeout - 1
        
        raise TimeoutException("wait_for_prompt timed out. Read: %s" % read)
    
