#!/usr/bin/env python

"""
Makes an attempt to contextualize to a VM.
In the beginning phase, only the user's public keys are loaded into the target VM.

@date: July 2, 2014
@author: CarolinaFernandez, omoya
"""

import os
import paramiko
#import subprocess
from Crypto import Random
from paramiko_scp.scp import SCPClient


class VMContextualize(object):

    def __init__(self, *args, **kwargs):
        self.vm_address = kwargs["vm_address"]
        self.vm_user = kwargs["vm_user"]
        self.vm_user_password = kwargs["vm_password"]

    def create_client(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Re-initialize RNG after fork to avoid connectivity problems with Paramiko
        Random.atfork()
        client.connect(self.vm_address, username=self.vm_user, port=22, password=self.vm_user_password)
        return client

    def copy(self, local_path, remote_path):
        client = self.create_client()
        scp_client = SCPClient(client.get_transport())
        scp_client.put(local_path, remote_path)

    def contextualize(self, context_command):
        client = self.create_client()
        a,b,c = client.exec_command(context_command)
 
    def contextualize_add_pub_keys(self, user_keys):
        current_folder = os.path.abspath(os.path.dirname(__file__))
        # Extra step (running script) for Debian6-like images
        fix_dep_script = os.path.join(current_folder, "fix_dependencies.bash")
        self.contextualize_script(fix_dep_script)
        self.run_script("fix_dependencies.bash")
        command = ""
        context_sudoers = ""
        users_sudoers = ""
        for user, keys in user_keys.iteritems():
            # Important: check for string "<user>:" (with two dots) to avoid match of substrings
            command += "( [[ -z $(grep '%s:' /etc/group) ]] && useradd %s -m -s /bin/bash ); \
                       mkdir -p /home/%s/.ssh; \
                       touch /home/%s/.ssh/authorized_keys; " % (user, user, user, user)
            command += "( [[ ! -z $(grep '%s:' /etc/group) ]] && chown %s:%s -R /home/%s ); " % (user, user, user, user)
            for key in keys:
                command += "( [[ -z $(grep '%s' /home/%s/.ssh/authorized_keys) ]] && echo '%s' >> /home/%s/.ssh/authorized_keys ); " % (key, user, key, user)
            users_sudoers += "%s ALL=NOPASSWD:ALL\n" % user
        # Edit sudoers file, add sudo package
        context_sudoers = open(os.path.join(current_folder, "contextualize_sudoers.txt")).read()
        context_sudoers = context_sudoers.replace("<%newuser1%>", "%s ALL=(ALL:ALL) ALL" % user)
        context_sudoers = context_sudoers.replace("<%newuser2%>", users_sudoers)
        command += "echo \"\"\"%s\"\"\" > /etc/sudoers; " % context_sudoers

        return self.contextualize(command)

    def contextualize_script(self, path):
        self.copy(path, "/opt/")

    def run_script(self, path):
        command = "chmod u+x /opt/%s; bash /opt/%s > /dev/null 2>&1 &" % (path, path)
        return self.contextualize(command)
