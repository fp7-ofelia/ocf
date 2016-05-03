#!/usr/bin/env python

"""
Storage of basic monitoring data per server: free HD size and memory.

@date: April 26, 2016
@author: CarolinaFernandez
"""

from datetime import datetime
from geniutils.src.xrn.xrn import hrn_to_urn
from geniutils.src.xrn.xrn import urn_to_hrn

import subprocess
import time

class ServerStats(object):
    """
    Module to retrieve free/total size of memory and HD disk.

    IMPORTANT: The host where this module is deployed must be able to
    access each virtualisation server through SSH public keys (i.e.
    no password / interaction required).

    IMPORTANT: Place the private key related to the accepted public
    IP in the folder defined by 'priv_key_path' and give read access
    to the user that runs the Apache process (e.g. 'www-data')
    """

    # NOTE: Change with the ssh port used in your XEN servers
    server_ssh_port = 7373
    #priv_key_path = "~/.ssh/id_rsa"
    priv_key_path = "/opt/ofelia/server_id_rsa"

    @staticmethod
    def create_client(address):
        from Crypto import Random
        import os
        import paramiko
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Re-initialize RNG after fork to avoid connectivity problems with Paramiko
        Random.atfork()
        privatekeyfile = os.path.expanduser(ServerStats.priv_key_path)
        key = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        #client.connect(address, username="root", password="<change_by_yours>", port=ServerStats.server_ssh_port)
        client.connect(address, username="root", pkey=key, port=ServerStats.server_ssh_port)
        return client

    @staticmethod
    def communicate(server, command_arg):
        output = None
        try:
            address = server.agentURL.split(":")[1].replace("//","")
            command = ['ssh', '-p%s' % ServerStats.server_ssh_port, 'root@' + address, '-t']
            #command_list = command_arg#.split(" ")
            #command.extend(command_list)
            #process = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #output, err = process.communicate()
            #output = output.translate(None, '\r\n')
            #errcode = process.returncode
            client = ServerStats.create_client(address)
            stdin, stdout, stderr = client.exec_command(command_arg)
            output = stdout.read()
            output = output.replace("\n", "")
            # print "Output: ", output
        except Exception as e:
            print "ServerStats: error accessing virtualisation server to retrieve stats. Details: %s", e
            import traceback
            traceback.print_exc()
        return output

    @staticmethod
    def get_free_hd(server):
        # Check HD usage (with units)
        #command = ['df', '-hl', '|', 'tail', '-1', '|', 'cut', '-d"G"', '-f3', '|', 'cut', '-d" "', '-f3', '|', 'cut', '-d"%"', '-f1']
        command = 'df -hl | tail -1 | cut -d"G" -f3 | cut -d" " -f3 | cut -d"%" -f1'
        return ServerStats.communicate(server, command)

    @staticmethod
    def get_total_hd(server):
        # Check HD usage (with units)
        #command_list = ['df', '-hl', '|', 'tail', '-1', '|', 'cut', '-d"G"', '-f1', '|', 'cut', '-d" "', '-f4', '|', 'cut', '-d"%"', '-f1']
        command = 'df -hl | tail -1 | cut -d"G" -f1 | cut -d" " -f4 | cut -d"%" -f1'
        return ServerStats.communicate(server, command)

    @staticmethod
    def get_free_hd_percent(server):
        # Check HD usage (in percent)
        #command = ['df', '-hl', '|', 'tail', '-1', '|', 'cut', '-d"G"', '-f4', '|', 'cut', '-d" "', '-f3', '|', 'cut', '-d"%"', '-f1']
        command = 'df -hl | tail -1 | cut -d"G" -f4 | cut -d" " -f3 | cut -d"%" -f1'
        return ServerStats.communicate(server, command)

    @staticmethod
    def get_free_memory(server):
        # Check free memory (in MB)
        #command = ['free', '-m', '|', 'grep', '"Mem:"', '|', 'awk', '\'BEGIN{print "free"} {free+=$4;} END{print free}\'', '|', 'column', '-t', '|', 'tail', '-1']
        #command = ['xm', 'info', '|', 'grep', '"free_memory"', '|', 'cut', '-d":"', '-f2', '|', 'column', '-t']
        command = 'xm info | grep "free_memory" | cut -d":" -f2 | column -t'
        return ServerStats.communicate(server, command)

    @staticmethod
    def get_total_memory(server):
        # Check total memory (in MB)
        #command = ['xm', 'info', '|', 'grep', '"total_memory"', '|', 'cut', '-d":"', '-f2', '|', 'column', '-t']
        command = 'xm info | grep "total_memory" | cut -d":" -f2 | column -t'
        return ServerStats.communicate(server, command)

    @staticmethod
    #def update_server_with_hd_and_memory(server, vm_hd_mb, vm_memory_mb):
    def update_server_with_hd_and_memory(server_and_data):
        # NOTE: Updated VM HD and memory must be provided signed
        #  i.e. "-" when allocating/provisioning, "+" when deleting
        server = server_and_data["server"]
        vm_hd_mb = server_and_data["vm_hd_mb"]
        vm_memory_mb = server_and_data["vm_memory_mb"]
        free_hd = ServerStats.get_free_hd(server)
        free_mem = ServerStats.get_free_memory(server)
        # NOTE: HD size from server is in GB, HD size in argument is in MB
        try:
            # TODO: Fix storage of values (currently not updating!)
            server.setDiscSpaceGB(float(free_hd) + (float(vm_hd_mb)/1024))
            server.save()
            server.setMemory(int(free_mem) + int(vm_memory_mb))
            server.save()
        except Exception as e:
            print "ServerStats: error updating server status on free disk and memory. Details: %s", e
            # print "server: ", server
            # print "free_hd: ", free_hd
            # print "free_mem: ", free_mem
            import traceback
            traceback.print_exc()
