#!/usr/bin/python

"""
Makes an attempt to contextualize to a VM.
In the beginning phase, only the user's public keys are loaded into the target VM.

@date: July 2, 2014
@author: CarolinaFernandez
"""

import argparse
#from ConfigParser import ConfigParser
import pexpect

class VMContextualize(object):

    def __init__(self, *args, **kwargs):
        self.vm_address = kwargs["vm_adress"]
        self.vm_user = kwargs["vm_user"]
        self.vm_user_password = kwargs["vm_password"]
    
    def ssh(self, context_command):
        #command = "ssh {0} \"%s\"" % str(args)
        #command = "ssh {0} \"%s\"".format("%s@%s" % (self.vm_user, self.vm_address)) % context_command
        command = "ssh %s@%s \"%s\"" % (self.vm_user, self.vm_address, context_command)
        return command
    
    def vm_ssh_access(self, context_command):
        #url = args.url
        #root_user, host = url.split("@", 1)
        #cfg_file = "vm_ssh.conf"
        #cfg = ConfigParser()
        #cfg.read(cfg_file)
        #root_password = cfg.get(root_user, host)
        #root_password = "openflow"
        child = pexpect.spawn(self.ssh(context_command))
        child.expect("password:")
        child.sendline(self.vm_user_password)
        return child.interact()
    
    def contextualize(self, context_command):
        try:
            return self.vm_ssh_access(context_command)
        except Exception as e:
            print "VMContextualize exception: %s" % str(e)

    def contextualize_add_pub_key(self, user, key):
        #TODO: Place in a new class that inherits from VMContextualize
        commands = []
        # Below results to be created only if not already exist
        commands.append("useradd %s -m -s /bin/bash" % user)
        commands.append("mkdir /home/%s/.ssh" % user)
        commands.append("touch /home/%s/.ssh/authorized_keys" % user)
        commands.append("if [ -z $(grep '%s' /home/%s/.ssh/authorized_keys ) ]; then echo '%s' >> /home/%s/.ssh/authorized_keys; fi" % (key, user, key, user))
        command = "; ".join(commands)
        return self.contextualize(command)

if __name__ == '__main__':
    # With arguments
    parser = argparse.ArgumentParser(description='Run ssh through pexpect')
    parser.add_argument("--address", metavar="a", type=str, required=False,
        help="Address of the VM")
    parser.add_argument("--user", metavar="u", type=str, required=False,
        help="User of the VM")
    parser.add_argument("--password", metavar="p", type=str, required=False,
        help="Password for the user of the VM")
    args = parser.parse_args()
    # Or using kwargs
    params = {
                "vm_adress": args.address or "10.216.12.28",
                "vm_user": args.user or "root",
                "vm_password": args.password or "openflow",
            }
    vm_context = VMContextualize(**params)
    vm_context.contextualize_add_pub_key("carolina", open("/home/carolina/.ssh/id_dsa.pub").read())
