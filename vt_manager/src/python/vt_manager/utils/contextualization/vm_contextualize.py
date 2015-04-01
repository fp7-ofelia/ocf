#!/usr/bin/env python

"""
Makes an attempt to contextualize to a VM.
In the beginning phase, only the user's public keys are loaded into the target VM.

@date: July 2, 2014
@author: CarolinaFernandez, omoya
"""

import os
import paramiko
from Crypto import Random


class VMContextualize(object):

    def __init__(self, *args, **kwargs):
        self.vm_address = kwargs["vm_address"]
        self.vm_user = kwargs["vm_user"]
        self.vm_user_password = kwargs["vm_password"]
    
    def contextualize(self, context_command):
        client =  paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.vm_address, username=self.vm_user, port=22, password=self.vm_user_password)
        a,b,c = client.exec_command(context_command)
    
    def contextualize_add_pub_key(self, user, key):
        command = "useradd %s -m -s /bin/bash && \
                   mkdir -p /home/%s/.ssh && \
                   touch /home/%s/.ssh/authorized_keys && \
                   if [ -z $(grep '%s' /home/%s/.ssh/authorized_keys) ]; then echo '%s' >> /home/%s/.ssh/authorized_keys; fi && \
                   chown %s:%s -R /home/%s" % (user, user, user, key, user, key, user, user, user, user) # Cheat code :)
        # Edit sudoers file, add sudo package
        current_folder = os.path.abspath(os.path.dirname(__file__))
        context_sudoers = open(os.path.join(current_folder, "contextualize_sudoers.txt")).read()
        context_sudoers = context_sudoers.replace("<%newuser%>", "%s ALL=NOPASSWD:ALL" % user)
        # Do not change ANYTHING from the next command lines. If needed, extend contents of 'command' variable
        command += "; echo \"\"\"%s\"\"\" > /etc/sudoers && \
                    aptitude update && \
                    aptitude install sudo > /dev/null 2>&1 &" % context_sudoers
        return self.contextualize(command)
