#!/usr/bin/env python

"""
Makes an attempt to contextualize to a VM.
In the beginning phase, only the user's public keys are loaded into the target VM.

@date: July 2, 2014
@author: CarolinaFernandez, omoya
"""

#import argparse
#import pexpect
import paramiko
from Crypto import Random


class VMContextualize(object):

    def __init__(self, *args, **kwargs):
        self.vm_address = kwargs["vm_address"]
        self.vm_user = kwargs["vm_user"]
        self.vm_user_password = kwargs["vm_password"]
        self.ssh_client = None
    
    def ssh(self, context_command):
        #command = "ssh {0} \"%s\"" % str(args)
        #command = "ssh {0} \"%s\"".format("%s@%s" % (self.vm_user, self.vm_address)) % context_command
        # Avoid checking key fingerprint for the connected VM
        #ssh_options = "-q -o BatchMode=yes -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -l"
        ssh_options = "-q -o StrictHostKeyChecking=no -l"
        command = "ssh %s %s %s -t \"%s\"" % (ssh_options, self.vm_user, self.vm_address, context_command)
        return command
    
    def vm_ssh_access(self, context_command):
        #child = pexpect.spawn(self.ssh(context_command))
        #child.expect("password:")
        #child.sendline(self.vm_user_password)
        #return child.interact()
        # Hack: randomize before paramiko runs to avoid a bug when launching this with multiprocessing
        Random.atfork()
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.load_system_host_keys()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(self.vm_address,username=self.vm_user, password=self.vm_user_password)
        channel = self.ssh_client.invoke_shell()
        stdin = channel.makefile("wb")
        stdout = channel.makefile("rb")
        stdin.write(context_command)
        output = stdout.read()
        #print output
        stdout.close()
        stdin.close()

    def contextualize(self, context_command):
        exec_ok = True
        try:
            self.vm_ssh_access(context_command)
        except Exception as e:
            exec_ok = False
        finally:
            # Either with or without errors, check SSH client and close when necessary
            if self.ssh_client:
                self.ssh_client.close()
        return exec_ok
    
    def contextualize_add_pub_key(self, user, key):
        #TODO: Place in a new class that inherits from VMContextualize
        commands = []
        # Below results to be created only if not already exist
        commands.append("useradd %s -m -s /bin/bash" % user)
        commands.append("mkdir -p /home/%s/.ssh" % user)
        commands.append("touch /home/%s/.ssh/authorized_keys" % user)
        commands.append("if [ -z $(grep '%s' /home/%s/.ssh/authorized_keys ) ]; then echo '%s' >> /home/%s/.ssh/authorized_keys; fi" % (key, user, key, user))
        commands.append("chown %s:%s -R /home/%s" % (user, user, user))
        # Get out from the interactive mode
        commands.append("exit\n")
        # Use commands separated by newline to enable multiple commands being issued at a time
        command = "\n".join(commands)
        return self.contextualize(command)
