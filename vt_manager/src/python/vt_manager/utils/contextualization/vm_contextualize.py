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
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.vm_address, username=self.vm_user, port=22, password=self.vm_user_password)
        a,b,c = client.exec_command(context_command)
   
    def contextualize_add_pub_keys(self, user_keys):
        command = ""
        context_sudores = ""
        for user, keys in user_keys.iteritems():
            command += "( [[ -z $(grep '%s' /etc/group) ]] && useradd %s -m -s /bin/bash ); \
                       mkdir -p /home/%s/.ssh; \
                       touch /home/%s/.ssh/authorized_keys; " % (user, user, user, user)
            for key in keys:
                command += "( [[ -z $(grep '%s' /home/%s/.ssh/authorized_keys) ]] && echo '%s' >> /home/%s/.ssh/authorized_keys ); " % (key, user, key, user)
            command += "chown %s:%s -R /home/%s; " % (user, user, user) # Cheat code :)

            # Edit sudoers file, add sudo package
            current_folder = os.path.abspath(os.path.dirname(__file__))
            context_sudoers = open(os.path.join(current_folder, "contextualize_sudoers.txt")).read()
            context_sudoers = context_sudoers.replace("<%newuser%>", "%s ALL=NOPASSWD:ALL" % user)
        # Some "tricks" to get a valid command
        command += "echo \"\"\"%s\"\"\" > /etc/sudoers && \
                    aptitude update && \
                    aptitude install sudo > /dev/null 2>&1 &" % context_sudoers
        return self.contextualize(command)
