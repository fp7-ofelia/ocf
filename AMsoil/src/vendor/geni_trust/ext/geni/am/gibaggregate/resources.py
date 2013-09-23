#----------------------------------------------------------------------
# Copyright (c) 2012-2013 Raytheon BBN Technologies
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and/or hardware specification (the "Work") to
# deal in the Work without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Work, and to permit persons to whom the Work
# is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Work.
#
# THE WORK IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE WORK OR THE USE OR OTHER DEALINGS
# IN THE WORK.
#----------------------------------------------------------------------

import sys
import stat
import os.path
import uuid

import config
import graphUtils 
from graphUtils import GraphNode

sliceURN = ""
sliceName = ""

class VMNode(GraphNode) :
    """ This class holds information about a VM (compute node) requested
        by an experimenter.

        Some information held by this class comes from the request 
        Rspec.  E.g. the experimenter specified name of the node. Other
        information held by this class is provide by this script.
        E.g. the OpenVZ container name that corresponds to this node.
    """
    numVMs = 6  # max number of Virtual Machines available from this aggregate

    def __init__(self, nodeNumber) :
        self.containerName = 100 + nodeNumber # OpenVZ container name (e.g. 101)
        self.controlNetAddr = ''        # IP address of node on control network
        self.nodeName = ''    # Experimenter supplied name (client_id)
        self.NICs = []        # List of NICs for this node
        self.installList = [] # List of files to be installed in VM during setup
        self.executeList = [] # List of commands to be executed on startup
        self.componentID = '' # component ID for the resource
        self.sliverURN = ''   # sliver urn

    def getNeighbors(self) :
        return self.NICs 

    def getNodeName(self) :
        return self.nodeName;


class NIC(GraphNode) :
    """ This class holds information about a NIC.  NICs are assoicated with
        a compute node (VMNode class).  The VMNode class keeps track of the
        NICs associated with a given VM.

        Some of the information held by this class comes from the request 
        Rspec.  E.g. the interface name used by the experimenter.
        Other information held by this class comes form this script.  E.g. 
        the IP address associated with the NIC.
    """
    def __init__(self) :
        self.nicName = ''         # Experimenter specified name for this NIC
        self.deviceNumber = ''    # Device num: 1 = eth1, 2 = eth2, 3 = eth3
        self.macAddress = ''      # MAC address for this NIC
        self.ipAddress = ''       # IP address associated with this NIC
        self.myHost = None;       # The host (VMNode) associated with this NIC
        self.virtualEthName = ''  # Name of corresponding VETH in the host OS
        self.link = None          # The link object associated with this NIC
        self.componentID = ''     # component ID for the resource
        self.sliverURN = ''       # sliver urn

    def getNeighbors(self) :
        return [self.link, self.myHost]
        
    def getNodeName(self) :
        return self.nicName;


class Link(GraphNode) :
    """ This class holds information about a link in the experimenter 
        specified network topology.  The NIC class keeps track of the link
        to which it is connected.

        Some of the information held by this class comes from the request
        Rspec.  E.g. the link name used by the experimenter. Other 
        information held by this class comes form this script.  E.g. the
        name of the host ethernet bridge associated with the NIC.
    """
    def __init__(self) :
        self.linkName = ''     # Experimenter specified name for this link
        self.subnetNumber = 0  # if subnetNumber is x, link is 10.0.x.0/24 
        self.bridgeID = ''     # Name of the host ethernet bridge associated
                               #  w/ the link (e.g. br3 for subnet 10.0.3.0/24)
        self.endPoints = []    # NICs at the end points of this link
        self.sliverURN = ''    # sliver urn

    def getNeighbors(self) :
        return self.endPoints

    def getNodeName(self) :
        return self.linkName;


class installItem :
    """
        VMNode maintains a list of files to be installed when the VM
        starts up.  Items in this list belong this class.
    """
    def __init__(self) :
        self.sourceURL = ''    # Location of file to be installed
        self.destination = ''  # Location in file system where file goes
        self.fileType = ''     # Type of file to be installed

class executeItem :
    """
        VMNode maintains a list of commands to be executed when the VM
        starts up.  Items in this list belong this class.
    """
    def __init__(self) :
        self.command = ''      # Command to be executed at VM startup
        self.shell = 'sh'      # Shell used to execute command


experimentHosts = {}    # Map of container names (e.g. 101) to corresponding
                        #    VMNode objects
experimentLinks = []    # List of links specified by the experimenter 
experimentNICs = {}     # Map of client supplied network interface names to
                        #    corresponding NIC objects

def _annotateGraph() :
    """ This function walks through the VMNode, NIC and LINK objects 
        created by parsing the request Rspec and fills in the missing
        information (e.g. MAC and IP addresses for interfaces, bridge names
        for links, etc).
    """
    # Walk though all NICs and assign them MAC addresses
    MACAddresses = [    # Table of MAC addresses for assignment to NICs
    "00:0C:29:B4:DF:A7",
    "00:0C:29:69:1D:AB",
    "00:0C:29:C8:76:FD",
    "00:0C:29:71:BA:ED",
    "00:0C:29:B8:81:05",
    "00:0C:29:9B:6E:5A",
    "00:0C:29:87:F0:5E",
    "00:0C:29:E8:77:47",
    "00:0C:29:7D:99:5C",
    "00:0C:29:3B:CF:F8",
    "00:0C:29:3E:76:6B",
    "00:0C:29:D5:B2:C3",
    "00:0C:29:D8:CB:38",
    "00:0C:29:D5:B2:13",
    "00:0C:29:DA:3E:91",
    "00:0C:29:15:97:46",
    "00:0C:29:AF:FC:08",
    "00:0C:29:05:DF:8C"
    ]
    macAddressesIndex = 0;
    nicNames = experimentNICs.keys()
    for i in range(len(nicNames)) :
        nicObject = experimentNICs[nicNames[i]]
        nicObject.macAddress = MACAddresses[macAddressesIndex];
        macAddressesIndex += 1

    # For every host, give its NICs numbers: 1 (= eth1), 2 or 3
    #    Also give the NICs the names of the corresponding veth device in the
    #    host.  OpenVZ convention: veth101.1 is virtual ethernet on host that
    #    corresponds to eth1 on container 101; veth103.2 is virtual ethernet
    #    on host that corresponds to eth2 on container 103.
    hostNames = experimentHosts.keys()
    for i in range(len(hostNames)) :
        hostObject = experimentHosts[hostNames[i]]
        interfaceCount = 1
        for nicObject in hostObject.NICs :
            nicObject.deviceNumber = interfaceCount
            nicObject.virtualEthName = 'veth%d.%d' % \
                (nicObject.myHost.containerName, interfaceCount)
            interfaceCount += 1

    # Give each link a subnet address and bridge name
    networkNumber = 3;   # Subnet number to assign to link. Starts with 3
                         #    since subnet 1 is for control network and 
                         #    subnet 2 is used by VirtualBox
    for i in range(len(experimentLinks)) :
        linkObject = experimentLinks[i]
        linkObject.subnetNumber = networkNumber
        linkObject.bridgeID = 'br%d' % networkNumber

        # Assign IP address to endpoints associated with the link
        #    IP address is of the form 10.0.networkNumber.VMNodeContainerName
        #    E.g. net num 3 attached to NIC on container 101 would be 10.0.3.101
        for j in range(0, len(linkObject.endPoints)) :
            nicObject = linkObject.endPoints[j]
            nicObject.ipAddress = "10.0.%d.%d" % (networkNumber, \
                nicObject.myHost.containerName)

        networkNumber += 1

    # Assign URNs to the VM resources
    for i in range(len(hostNames)) :
        hostObject = experimentHosts[hostNames[i]]
        hostObject.componentID = ('urn:publicid:IDN+geni-in-a-box.net+node+pc%s'
                                 % hostObject.containerName)
        hostObject.sliverURN = ('urn:publicid:IDN+geni-in-a-box.net+sliver+%s'
                                % hostObject.containerName)
        
    # Assign URNs to the NICs 
    for i in range(len(nicNames)) :
        nicObject = experimentNICs[nicNames[i]]
        nicObject.componentID =  \
            ('urn:publicid:IDN+geni-in-a-box.net+interface+pc%s:eth%s' % 
             (nicObject.myHost.containerName, nicObject.deviceNumber))
        nicObject.sliverURN = ('urn:publicid:IDN+geni-in-a-box.net+sliver+%s%s'
                               % (nicObject.myHost.containerName,
                                  nicObject.deviceNumber))

    # Assign URNs to the links 
    for i in range(len(experimentLinks)) :
        linkObject = experimentLinks[i]
        linkObject.sliverURN =  \
            'urn:publicid:IDN+geni-in-a-box.net+sliver+%s' % linkObject.bridgeID



def _generateBashScript(users) :
    ''' Generate the Bash script that is run to actually create and set up the
            Virtual Machines and networks used in the experiment.
    '''
    # Create the file into which the script will be written
    pathToFile = config.sliceSpecificScriptsDir + '/' + config.shellScriptFile
    try:
        scriptFile = open(pathToFile, 'w')
    except IOError:
        config.logger.error("Failed to open file that creates sliver: %s" %
                            pathToFile)
        return None

    # Make this file executable
    os.chmod(pathToFile, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    
    # Start creating the script
    scriptFile.write('#!/bin/bash \n\n')

    scriptFile.write('# This script is auto-generated by the aggregate\n')
    scriptFile.write('#    manager in response to a createSliver call \n\n')

    scriptFile.write('## Function definitions\n')
    scriptFile.write('pingNode () {  # pings specified PC to check if it is alive \n')
    scriptFile.write('    pingAttempts=0 \n')
    scriptFile.write('    echo \"Pinging VM 10.0.1.$1...\" \n')
    scriptFile.write('    ping -c2 10.0.1.$1 \n')
    scriptFile.write('    while [ $? -ne 0 ] && [ $pingAttempts -le 50 ] \n')
    scriptFile.write('    do \n')
    scriptFile.write('        sleep 10  # sleep for 10 more seconds \n')
    scriptFile.write('        let \"pingAttempts += 1\" \n')
    scriptFile.write('        echo \"Pinging VM 10.0.1.$1...\" \n')
    scriptFile.write('        ping -c2 10.0.1.$1 \n')
    scriptFile.write('    done \n')
    scriptFile.write('    if [ $pingAttempts -gt 20 ] \n')
    scriptFile.write('    then \n')
    scriptFile.write('        return 1  # failed to ping PC \n')
    scriptFile.write('    else \n')
    scriptFile.write('        return 0  # success \n')
    scriptFile.write('    fi \n')
    scriptFile.write('} \n')

    scriptFile.write('\n## Delete any existing sliver. \n')
    scriptFile.write('%s/%s %s %s\n' % (config.standardScriptsDir,
                                        config.deleteSliver,
                                        config.homeDirectory,
                                        config.sliceSpecificScriptsDir))

    hostNames = experimentHosts.keys()

    # Set the sliver status for each host to "unknown"
    scriptFile.write('\n# Setting sliver status of hosts to unknown \n')
    for i in range(len(hostNames)) :
        hostObject = experimentHosts[hostNames[i]]
        statusFileName = '%s/pc%s.status' % (config.sliceSpecificScriptsDir, 
                                             hostObject.containerName)
        scriptFile.write('echo \"unknown\" > %s \n' % statusFileName)
    

    # Create container templates
    scriptFile.write('\n## Define containers for each of the hosts in the experiment.\n')
    for i in range(len(hostNames)) :
        hostObject = experimentHosts[hostNames[i]]

        if config.distro == 'UBUNTU10-STD' : 
            scriptFile.write('vzctl create %s --ostemplate ubuntu-10.04-x86\n' % hostObject.containerName)
        else :
            scriptFile.write('vzctl create %s --ostemplate fedora-15-x86 --config basic\n' % hostObject.containerName)
            
    scriptFile.write('\n## Set up host names and control network IP addresses for the containers. \n')
    for i in range(len(hostNames)) :
        hostObject = experimentHosts[hostNames[i]]
        scriptFile.write('vzctl set %s --hostname %s --save \n' % 
                         (hostObject.containerName, hostObject.nodeName))
        scriptFile.write('vzctl set %s --ipadd 10.0.1.%s --save\n' %
                         (hostObject.containerName, hostObject.containerName))


    scriptFile.write('\n# Turn off firewall on host \n')
    scriptFile.write('/etc/init.d/iptables stop \n')

    scriptFile.write('\n## Set up interfaces on the hosts and connect them to the appropriate bridges \n')
    for i in range(len(hostNames)) :
        hostObject = experimentHosts[hostNames[i]]
        scriptFile.write('# Set up interfaces for host %s \n' % 
                         hostObject.nodeName)
        
        # for each NIC on host set up the interface
        for j in range(0, len(hostObject.NICs)) :
            nicObject = hostObject.NICs[j]
            scriptFile.write('vzctl set %d --netif_add eth%d,%s,%s,FE:FF:FF:FF:FF:FF,%s --save \n' % (hostObject.containerName, nicObject.deviceNumber, nicObject.macAddress, nicObject.virtualEthName, nicObject.link.bridgeID))
        scriptFile.write('\n')

    scriptFile.write('\n## Start up the hosts (containers) \n')
    for i in range(len(hostNames)) :
        hostObject = experimentHosts[hostNames[i]]
        scriptFile.write('vzctl start %s \n' % hostObject.containerName)
        
    scriptFile.write('\n## Configure bridges on host \n')
    for i in range(len(experimentLinks)) :
        linkObject = experimentLinks[i]
        scriptFile.write('brctl addbr %s \n' % linkObject.bridgeID)
        
        # Add the virtual eth devices corresponding to the end-points of the
        #    link to the bridge
        for j in range(len(linkObject.endPoints)) :
            scriptFile.write('brctl addif %s %s \n' % (linkObject.bridgeID, \
                                       linkObject.endPoints[j].virtualEthName))
        
        scriptFile.write('ifconfig %s 0 \n\n' % linkObject.bridgeID)
                             
    scriptFile.write('\n## Give the hosts 30 seconds to start up \n')
    scriptFile.write('sleep 30 \n\n')
    scriptFile.write('# Ping hosts to make sure they are up.  Give them more time if necessary.\n')
    for i in range(len(hostNames)) :
        hostObject = experimentHosts[hostNames[i]]
        scriptFile.write('pingNode %d \n' % hostObject.containerName)
        scriptFile.write('if [ $? -ne 0 ] \n')
        scriptFile.write('then \n')
        scriptFile.write('    echo \"Container %d failed to start up.\" \n' % hostObject.containerName)
        statusFileName = '%s/pc%s.status' % (config.sliceSpecificScriptsDir, 
                                             hostObject.containerName)
        scriptFile.write('    echo \"failed\" > %s \n' % statusFileName)
        scriptFile.write('else \n')
        statusFileName = '%s/pc%s.status' % (config.sliceSpecificScriptsDir, 
                                             hostObject.containerName)
        scriptFile.write('    echo \"configuring\" > %s \n' % statusFileName)
        scriptFile.write('fi \n')
        
    scriptFile.write('\n## Set up interfaces on each host (container) \n')
    for i in range(len(hostNames)) :
        hostObject = experimentHosts[hostNames[i]]
        scriptFile.write('# Set up interfaces on PC %s\n' % hostObject.nodeName)
        
        # Set up ethernet devices on the container
        for j in range(len(hostObject.NICs)) :
            scriptFile.write('vzctl exec %d \"/sbin/ifconfig eth%d 0\" \n' % \
                                 (hostObject.containerName, \
                                 hostObject.NICs[j].deviceNumber))
            scriptFile.write('vzctl exec %d \"/sbin/ip addr add %s dev eth%d\"\n'  % \
                                 (hostObject.containerName, \
                                 hostObject.NICs[j].ipAddress, \
                                 hostObject.NICs[j].deviceNumber))
            scriptFile.write('vzctl exec %d \"echo 0 > /proc/sys/net/ipv4/conf/eth%d/rp_filter\" \n' \
                             % (hostObject.containerName, \
                                hostObject.NICs[j].deviceNumber))
            scriptFile.write('vzctl exec %d \"/sbin/ifconfig eth%d up\" \n' % \
                                 (hostObject.containerName, \
                                 hostObject.NICs[j].deviceNumber))
            scriptFile.write('\n')


    # Now we are ready to set up the IP routing tables on each container
    scriptFile.write('\n## Set up IP routing tables on each host \n');
    for i in range(len(hostNames)) :
        hostObject = experimentHosts[hostNames[i]]
    
        scriptFile.write('# Set up IP routing table for %s\n' % \
                             hostObject.nodeName)

        # Turn on IP forwarding so host (container) can forward IP packets
        scriptFile.write('vzctl exec %d \"/sbin/sysctl -w net.ipv4.ip_forward=1\" \n' \
                         % hostObject.containerName)

        ## Now set up routing tables.  Create routing table entries so we
        #    can get to any reachable link (subnet) from this host.
        #  We first set up routes to links that are directly connected to
        #    to this host.  Then we set up routes to links that can be
        #    reached through a gateway.
	
        #  Make two lists: One of directly connected links and the other
        #    that are not directly connected
        #
        directlyConnectedLinks = []
        notDirectlyConnectedLinks = []
        for j in range(len(experimentLinks)) :
            directlyConnected = False
            linkObject = experimentLinks[j]
            for k in range(len(linkObject.endPoints)) :
                if linkObject.endPoints[k].myHost == hostObject :
                    # This host is directly connected to the link (subnet)
                    #    because one of the endPoints (NICs) on this link
                    #    belong to this host.
                    directlyConnected = True

            if directlyConnected :
                directlyConnectedLinks.append(linkObject)
            else :
                notDirectlyConnectedLinks.append(linkObject) 
        
        # Now set up routing table entries for directly connected links.
        #   For these links we simply route packets to the NIC on this
        #   host that is conneted to this link (subnet) 
	for j in range(len(directlyConnectedLinks)) :
            linkObject = directlyConnectedLinks[j]

            # Find the endpoint on this link that is connected to this host
            for k in range(len(linkObject.endPoints)) :
                if linkObject.endPoints[k].myHost == hostObject :
                    # Found the endPoint (NIC) connects this host to the link
                    endPointToLink = linkObject.endPoints[k]
                    scriptFile.write('vzctl exec %d \"/sbin/ip route add 10.0.%d.0/24 dev eth%d\" \n' \
                                     % (hostObject.containerName, \
                                        linkObject.subnetNumber, \
                                         endPointToLink.deviceNumber))
                    break    # Break out of the 'for k in...' loop
            
        # Now set up routing table entries for links that are not directly
        #    connected.  For these links find the shortes path to the link
        #    (subnet) and route packes in that direction (first host in that
        #    direction acts as a gateway)
        for j in range(len(notDirectlyConnectedLinks)) :
            linkObject = notDirectlyConnectedLinks[j]

            # Find the shortest path from this host to this subnet (linkObject)
            path = graphUtils.findShortestPath(hostObject, linkObject)
            if path != None :
                # We found a path from this host to the subnet (link)
                #    Path is a NIC -> Link -> NIC -> Host (gateway) -> ...
                #    We care about the NIC on the gateway i.e. the 3rd
                #    item on this path
                scriptFile.write('vzctl exec %d \"/sbin/ip route add 10.0.%d.0/24 via %s\" \n' \
                                 % (hostObject.containerName, \
                                    linkObject.subnetNumber, \
                                     path[3].ipAddress))

        scriptFile.write('\n')

    # Turn on forwarding and arp proxing on the virtual eth devices created
    #    in the host OS (container 0)
    scriptFile.write('\n# Turn on forwarding and arp proxing on the virtual eth devices created on the host OS \n')
    nicNames = experimentNICs.keys()
    for i in range(len(nicNames)) :
        nicObject = experimentNICs[nicNames[i]]
        scriptFile.write('ifconfig %s 0 \n' % nicObject.virtualEthName)
        scriptFile.write('echo 1 > /proc/sys/net/ipv4/conf/%s/forwarding \n' \
                             % nicObject.virtualEthName)
        scriptFile.write('echo 1 > /proc/sys/net/ipv4/conf/%s/proxy_arp \n' \
                             % nicObject.virtualEthName)
        scriptFile.write('\n')

    # Set up DNS entries on the containers so they can reference one another
    #    by name and can also reference hosts on the external network by name
    scriptFile.write('\n# Set up DNS on the hosts.  Use Google DNS.\n')
    scriptFile.write('PRIMARYDNS=\"nameserver 8.8.8.8\" \n')
    scriptFile.write('SECONDARYDNS=\"nameserver 8.8.4.4\" \n')
    for i in range(len(hostNames)) :
        hostObject = experimentHosts[hostNames[i]]
        scriptFile.write('vzctl exec %s \"echo order host,bind >> /etc/host.conf\" \n' % hostObject.containerName)
        scriptFile.write('vzctl exec %s \"echo $PRIMARYDNS >> /etc/resolv.conf\" \n' % hostObject.containerName)
        scriptFile.write('vzctl exec %s \"echo $SECONDARYDNS >> /etc/resolv.conf\" \n' % hostObject.containerName)
    scriptFile.write('\n')

    # Add hostname and IP addresses to /etc/hosts.  For each host we pick
    #    IP address to add to this file.  We arbitrarily pick the IP address
    #    associated with the first eth device in the list of NICs associated
    #    with the host.  Examples of how hosts can be addressed: client_id,
    #    pc101, client_id.sliceName.geni-in-a-box.net or 
    #    pc101.geni-in-a-box.net.
    scriptFile.write('# Add host names and IP addresses to /etc/hosts \n')
    for i in range(len(hostNames)) :
        hostObject = experimentHosts[hostNames[i]]
        # In the /etc/hosts for this host add an entry for every host
        for j in range(len(hostNames)) :
            hostObject2 = experimentHosts[hostNames[j]]
            if len(hostObject2.NICs) != 0 :
                scriptFile.write('vzctl exec %s \"echo %s %s pc%s %s.%s.geni-in-a-box.net pc%s.geni-in-a-box.net >> /etc/hosts\" \n' \
                                     % (hostObject.containerName, 
                                        hostObject2.NICs[0].ipAddress, 
                                        hostObject2.nodeName,
                                        hostObject2.containerName,
                                        hostObject2.nodeName,
                                        sliceName,
                                        hostObject2.containerName))

        # /etc/hosts has an entry for this host that is automatically 
        #    put in there by OpenVZ.  The entry looks like:
        #         10.0.1.101 hostName
        # We don't want this entry because is uses the control network. To
        #    delete this entry we copy /etc/hosts to /tmp/etc.hosts, delete
        #    the offending line, and write to /etc/hosts.  The offending
        #    line will always start with 10.0.1. (control network)
        scriptFile.write('# Deleting entry for %s that was inserted by OpenVz\n' % hostObject.nodeName)
        scriptFile.write('vzctl exec %s \"cp /etc/hosts /tmp/etc.hosts\"\n' 
                         % hostObject.containerName)
        scriptFile.write('vzctl exec %s \"cat /tmp/etc.hosts | sed \'/^10.0.1./d\' > /etc/hosts\" \n' % hostObject.containerName)
        scriptFile.write('vzctl exec %s \"rm /tmp/etc.hosts\" \n' %
                             hostObject.containerName)
        scriptFile.write('\n')
    
    
    # Download and install experimenter specified  files into the VMs
    # Go through each host and find out what needs to be installed
    for i in range(len(hostNames)) :
        hostObject = experimentHosts[hostNames[i]]
        installList = hostObject.installList
        if len(installList) != 0 :
            scriptFile.write('# Install experimenter specified software on host %s \n' % hostObject.nodeName)
        for item in installList :
            # Download the file from the specified URL
            scriptFile.write('# Download file %s\n' % item.sourceURL)
            scriptFile.write('wget -P /tmp %s \n' % item.sourceURL)
            scriptFile.write('if [ $? -eq 0 ] \n')
            scriptFile.write('then \n')
            scriptFile.write('    # Download successful \n')

            downloadedFile = '/tmp/%s' % os.path.basename(item.sourceURL)

            # Now generate commands to move the file to its proper location.
            #     If the file is of type .tgz or .tar.gz, we untar it to 
            #         the location specified by the experimenter.
            #     If the file is of type .gz, we copy the file to the 
            #         location specified by the experimenter and gunzip it there
            #     If the file is of some other type, we simply copy it to the
            #         location specified by the experimenter

            # First figure out file type
            if item.fileType == "" :
                #  File type not specified; guess based on file extension
                if item.sourceURL.endswith("tgz") or  \
                        item.sourceURL.endswith("tar.gz") :
                    # This is a tarball
                    item.fileType = "tar.gz"
                elif item.sourceURL.endswith("gz") :
                    # This is a gzip compressed file
                    item.fileType = "gz"
                else :
                    # Unknown or unsupported file type.  We simply copy
                    #    such a file to its install location
                    item.fileType = "unknown"

            # Now make sure destination path does not end with a / (unless it
            #    is the directory /)
            dest = item.destination
            if dest.endswith("/") and len(dest) > 1 :
                dest = dest[:-1]

            # The downloaded file is to be installed in the file system of 
            #    the appropriate container.  For e.g. file system for 
            #    container 101 is at /vz/root/101/...
            dest = ("/vz/root/%s" % hostObject.containerName) + dest

            # Create destination directory (and any necessary parent/ancestor
            #    directories in path) if it does not exist
            if not os.path.isdir(dest) :
                scriptFile.write('    mkdir -p %s \n' % dest)

            if item.fileType == 'tar.gz':
                # File to be installed is of type tar.gz: Uncompress and 
                #    untar to destination
                scriptFile.write('    tar -C %s -zxvf %s \n' % 
                                 (dest, downloadedFile))
            elif item.fileType == 'gz' :
                # File to be installed is of type gz: Copy to destination 
                #    and then gunzip in place
                scriptFile.write('    cp %s %s \n' % (downloadedFile, dest))
                # Get the name of the zipped file
                zipFile = dest + '/' + os.path.basename(downloadedFile)
                scriptFile.write('    gunzip %s \n' % zipFile)
            else :
                # Some other file type.  Simply copy file to destination
                scriptFile.write('    cp %s %s \n' % (downloadedFile, dest))

            # Make file accessible to experimenter
            scriptFile.write('    chmod -R 777 %s \n' % dest)

            # Delete the downloaded file
            scriptFile.write('    rm %s \n' % downloadedFile)

            scriptFile.write('fi \n')


        # Now handle scripts to be executed on host (container) startup
        execList = hostObject.executeList
        if len(execList) != 0 :
            scriptFile.write('\n# Set up experimenter specified startup scripts on host %s \n' % hostObject.nodeName)
        for item in execList :
            if item.shell == 'sh' or 'bash' :
                pathToScript = '/vz/root/%s/%s' % (hostObject.containerName,
                                                   item.command)
                scriptFile.write('vzctl runscript %s %s \n' % \
                                     (hostObject.containerName, pathToScript))
            else :
                # Not a script type we recognize.  Log error
                config.logger.error("Execute script %s is of unsuported type" \
                                        % item.command)

        scriptFile.write('\n')
        
        # set up an account for root
        scriptFile.write('# Create root account in container %i \n' %
                         hostObject.containerName)
        scriptFile.write('vzctl set %i --userpasswd root:%s \n' %
                         (hostObject.containerName, config.rootPwd))

        # set up the user accounts and ssh public keys 
        for user in users :
            userName = ""    # the current user the public key is installed for
            publicKeys = []  # the public keys for the current user, these are not files
            
            # go through every user and get the user's name and ssh public key
            for key in user.keys() :
                # found a user, there should only be one of these per key in 'user'
                if key == "urn" :
                    userName = user[key]
                    userName = userName.split("+")[-1]
                
                # found a new public key list, store all the public keys
                elif key == "keys" :
                    for value in user[key] :
                        publicKeys.append(value)
            
            # only install the user account if there is a user to install
            if userName != "":
                scriptFile.write("# Create user %s for container %i and install public keys\n" % (userName, hostObject.containerName))
                scriptFile.write("echo \"Creating user %s for container %s and installing public keys...\"\n" % (userName, hostObject.nodeName))
                scriptFile.write("vzctl set %i --userpasswd %s:%s \n" % 
                                 (hostObject.containerName,
                                  userName, config.rootPwd))
            
                # install all of the public keys for this user
                for publicKey in publicKeys :
                    scriptFile.write("mkdir -p /vz/root/%i/home/%s/.ssh\n" % (hostObject.containerName, userName))
                    scriptFile.write("chmod 755 /vz/root/%i/home/%s/.ssh\n" % (hostObject.containerName, userName))
                    scriptFile.write("touch /vz/root/%i/home/%s/.ssh/authorized_keys\n" % (hostObject.containerName, userName))
                    scriptFile.write("chmod 744 /vz/root/%i/home/%s/.ssh/authorized_keys\n" % (hostObject.containerName, userName))
                    scriptFile.write("echo \"%s\">>/vz/root/%i/home/%s/.ssh/authorized_keys\n" % (publicKey[:-1], hostObject.containerName, userName))

                # add this user to group wheel or root depending on OS
                groupName = ""
                if config.distro == 'UBUNTU10-STD' : 
                    groupName = "root"
                else :
                    groupName = "wheel"
                    
                scriptFile.write('vzctl exec %s \"usermod -a -G %s %s" \n' %
                                (hostObject.containerName, groupName, userName))
            
            scriptFile.write('\n')
            
        scriptFile.write('\n')

    scriptFile.close()


def specialFiles() :
    # Re-open the file containing the bash script in append mode
    pathToFile = config.sliceSpecificScriptsDir + '/' + config.shellScriptFile
    try:
        scriptFile = open(pathToFile, 'a')
    except IOError:
        config.logger.error("Failed to re-open file that creates sliver: %s" %
                            pathToFile)
        return None

    scriptFile.write('\n# Set up special files that contain slice info. \n')
    hostNames = experimentHosts.keys()
    for i in range(len(hostNames)) :
        hostObject = experimentHosts[hostNames[i]]
        
        # Put the slice manifest in the VMs 
        # Figure out name of destination directory for manifest.  Create that
        #    directory (and any necessary parent/ancestor directories in path) 
        #    if it does not exist
        scriptFile.write('# Put slice manifest in /proj/<siteName>/exp/<sliceName>/tbdata/geni_manifest \n')
        dest = '/vz/root/%s/proj/geni-in-a-box.net/exp/%s/tbdata/geni_manifest' % (hostObject.containerName, sliceName)
        scriptFile.write('mkdir -p %s \n' % dest)

        # Copy the manifest to this directory
        src = config.sliceSpecificScriptsDir + '/' +  config.manifestFile
        scriptFile.write('cp %s %s \n' % (src, dest))


        # Put slice information in /var/emulab/boot/nickname
        #    This file has the fully qualified name of the host in the form
        #    <experimenterSpecifiedHostName>.<sliceName>.geni-in-a-box.net
        scriptFile.write('# Create nickname file \n')
        dest = '/vz/root/%s/var/emulab/boot' %  \
            hostObject.containerName
        scriptFile.write('mkdir -p %s \n' % dest)

        fileContents = '%s.%s.geni-in-a-box.net' % (hostObject.nodeName,
                                                    sliceName)
        scriptFile.write('echo \"%s\" > %s/nickname \n' % (fileContents, dest))

        # Set status of the node to ready
        scriptFile.write('# Set node status to ready \n')
        statusFileName = '%s/pc%s.status' % (config.sliceSpecificScriptsDir, 
                                             hostObject.containerName)
        scriptFile.write('echo \"ready\" > %s \n' % statusFileName)

        scriptFile.write('\n')
        
    scriptFile.close()


def freeResources() :
    """
        Free up resources.
    """
    experimentHosts.clear()
    del experimentLinks[:]
    experimentNICs.clear()


def getResourceStatus() :
    """
        Return a list with the status of all VM resources.  Each item in the
        list is a dictionary with resource URN, resource status and error code.
        This is what the list looks like:
            [ { geni_urn: <resource URN>
                geni_status: <status: configuring, ready, failed or unknown>
                geni_error: <error code> }
              { geni_urn: <resource URN>
                geni_status: <status: configuring, ready, failed or unknown>
                geni_error: <error code> }
            ]
    """
    resStatus = list()
    hostNames = experimentHosts.keys()
    for i in range(len(hostNames)) :
        hostObject = experimentHosts[hostNames[i]]
        resStatusFile = '%s/pc%s.status' % (config.sliceSpecificScriptsDir, 
                                             hostObject.containerName)
        try :
            f = open(resStatusFile, 'r')
            resStatus.append(dict(geni_urn = hostObject.sliverURN,
                                  geni_status = f.readline().strip('\n'),
                                  geni_error = ''))
            f.close()
        except :
            resStatus.append(dict(geni_urn = hostObject.sliverURN,
                                  geni_status = "unknown",
                                  geni_error = ''))

    return resStatus



def provisionSliver(users) :
    """
        Provision the sliver.  First fill in missing information in the
        VMNode, NIC and Link objects created when parsing the request rspec.
        Then generate the bash script that, when run, will create and configure
        the OpenVZ containers.
    """
    # Fill in missing information in VMNode, NIC and Link objects
    _annotateGraph()

    # Generate the bash script
    _generateBashScript(users)
    
