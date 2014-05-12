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
import datetime
import re
from xml.dom.minidom import *

import config
import resources
from resources import VMNode, NIC, Link, installItem, executeItem, \
    experimentHosts, experimentLinks, experimentNICs 

def parseRequestRspec(slice_urn, rspec) :
    """ This function parses a request Rspec and creates an in-memory 
        representation of the experimenter specified topology using 
        VMNode, NIC and Link objects.

        This function returns None if everything goes well.  In case of
        of an error it returns a string describing the error.
    """
    # Get the slice name.  This is the last part of the URN.  For example,
    #    the slice name in the URN urn:publicid:IDN+geni:gpo:gcf+slice+myslice
    #    is myslice.
    resources.sliceURN = slice_urn
    resources.sliceName = re.split(r'[:\+]+', slice_urn)[-1]

    # Parse the xml rspec
    rspec_dom = parseString(rspec)

    # Look for DOM objects tagged 'node'.  These are hosts requested by the 
    #    experimenter
    hostList = rspec_dom.getElementsByTagName('node')

    # For each host, extract experimenter specified information from DOM node
    hostCount = 0;      # Keep track of the number of hosts allocated
    for host in hostList : 
        hostCount += 1
        if hostCount >  VMNode.numVMs :
            config.logger.error('Experimenter requested more nodes than available')
            return 'Number of nodes requested exceeds availability.  Number of nodes available: %s' % VMNode.numVMs 

        # Create a VMNode object for this host and add it to our collection
        #    of hosts allocated to the experiment
        hostObject = VMNode(hostCount)
        experimentHosts[hostObject.containerName] = hostObject

        # Get information about the host from the rspec
        hostAttributes = host.attributes   # DOM attributes object 
                                           #    associated with the host
        if hostAttributes.has_key('client_id') :
            hostObject.nodeName = hostAttributes['client_id'].value

        # Get interfaces associated with the host
        netInterfaceList = host.getElementsByTagName('interface')
        interfaceCount = 0;   # Track num of interfaces requested for this node
        for netInterface in netInterfaceList :
            interfaceCount += 1
            if interfaceCount > 3 :
                config.logger.error('Exceeded number of interfaces available on node')
                return 'Attempted to request a node with more than three interfaces.'
            
            # Create a NIC object for this interface and add it to the list 
            #    of NICs associated with this hostObject
            nicObject = NIC()
            hostObject.NICs = hostObject.NICs + [nicObject]
            nicObject.myHost = hostObject

            # Get information about the interface from the rspec
            nicAttributes = netInterface.attributes 
            if not nicAttributes.has_key('client_id') :
                config.logger.error('Network interface does not have a name')
                return 'Un-named network interface.  Make sure all interfaces in the request rspec have a client_id attribute.'

            nicObject.nicName = nicAttributes['client_id'].value
            experimentNICs[nicObject.nicName] = nicObject    # Add to 
                                  # collection of NICs used by this experiment

        # Get information on services to be performed on the host before
        #    it is ready for the experimenter.  
        servicesList = host.getElementsByTagName('services')
        for serviceElement in servicesList :
            installElements = serviceElement.getElementsByTagName('install')
            for item in installElements :
                installAttributes = item.attributes
                if not (installAttributes.has_key('url') and 
                        installAttributes.has_key('install_path')) :
                    config.logger.error('Source URL or destination path missing for install element in request rspec')
                    return 'Source URL or destination path missing for install element in request rspec'
                
                instItem = installItem()
                instItem.sourceURL = installAttributes['url'].value
                instItem.destination = installAttributes['install_path'].value
                if installAttributes.has_key('file_type') :
                    instItem.fileType = installAttributes['file_type'].value
                hostObject.installList = hostObject.installList + [instItem]
                
        for serviceElement in servicesList :
            executeElements = serviceElement.getElementsByTagName('execute')
            for item in executeElements :
                executeAttributes = item.attributes
                if not executeAttributes.has_key('command') :
                    config.logger.error('Command missing for execute element in request rspec')
                    return 'Command attribute missing for execute element in request rspec'
                
                execItem = executeItem()
                execItem.command = executeAttributes['command'].value
                if executeAttributes.has_key('shell') :
                    execItem.shell = executeAttributes['shell'].value
                hostObject.executeList = hostObject.executeList + [execItem]
                
    # Done getting information on hosts (nodes) requsted by experimenter.
    # Now get information about links.
    linksList = rspec_dom.getElementsByTagName('link')
    for link in linksList :
        linkObject = Link()    # Create a Link object for this link

        # Get attributes about this link from the rspec
        linkAttributes = link.attributes    # DOM attributes object 
                                            #    associated with link
        if not linkAttributes.has_key('client_id') :
            config.logger.error('Link does not have a name')
            return 'Un-named link.  Make sure all links in the request rspec have a client_id attribute.'

        linkObject.linkName = linkAttributes['client_id'].value
        experimentLinks.append(linkObject) # Add to collection of links 
                                           #    used by this experiment
        
        # Get the end-points for this link.  
        endPoints = link.getElementsByTagName('interface_ref');
        for i in range(len(endPoints)) :
            endPointAttributes = endPoints[i].attributes  # DOM attributes
                                           # object associated with end point
            interfaceName = endPointAttributes['client_id'].value  # Name of
                                    # the NIC that forms one end of this link
            
            # Find the NIC Object that corresponds to this interface name
            nicObject = experimentNICs[interfaceName]

            # Set the NIC Object to point to this link object
            nicObject.link = linkObject

            # Add this NIC Object to the list of end points for the link
            linkObject.endPoints = linkObject.endPoints + [nicObject]
            
    return None  # Success




"""\
Class for creating manifest files from a parsed request rspec.
"""
class GeniManifest :
    
    """\
    Static members of GeniManifest.
    
    These are used to specify various things about the manifest when it is
    created, typically the element tags, but also includes some hard coded
    element values such as the webpage
    """
    headerTag           = "rspec"                   # outer level node for the manifest file
    typeTag             = "type"                    # the type of manifest this was, only available is request
    xmlnsTag            = "xmlns"                   # xml name space tag
    expiresTag          = "expires"                 # the rpsec block specifying how long the manifest is good for
    nodeTag             = "node"                    # tag for node/host element
    exclusiveTag        = "exclusive"               # tag for specifying exclusivity of a host
    interfaceRefTag     = "interface_ref"           # tag for creating an interface element for a link
    interfaceTag        = "interface"               # tag for creating interfaces for a host
    componentIdTag      = "component_id"            # component id for resource
    sliverIdTag         = "sliver_id"               # sliver id for resource
    clientIdTag         = "client_id"               # experimenter specified id for resource
    linkTag             = "link"                    # tag for links added to the manifest
    macTag              = "mac_address"             # tag for mac addresses on interfaces
    ipAddressTag        = "ip_address"              # the ip address for an interface reference
    ipTag               = "ip"                      # used for creating an ip element for a node
    addressTag          = "address"                 # used for creating an address for an ip for a node
    componentManagerTag = "component_manager"       # tag used for a component manager sub-element
    componentManagerIdTag = "component_manager_id"  # tag used for component manager attributes on nodes
    sliverTypeTag       = "sliver_type"             # tag used for defining a sliver type on a host
    diskImageTag        = "disk_image"              # tag used for defining the type of image on a host
    servicesTag         = "services"                # tag used for defining services on a host node
    nameTag             = "name"                    # tag used for naming attributes
    hostTag             = "host"                    # used for identifying host elements under node elements
    rsVnodeTag          = "rs:vnode"                # used for identifying rs:vnode elements
    rsnsTag             = "xmlns:rs"                # name space for rs:
    loginTag            = "login"                   # tag used for specifying login info under the services element
    authenticationTag   = "authentication"          # tag used for attributes under login elements
    hostNameTag         = "hostname"                # tag used for attributes under login elements
    userNameTag         = "username"                # tag used for attributes under login elements
    portTag             = "port"                    # tag used for attributes under login elements
    webpage             = "http://www.protogeni.net/resources/rspec/0.1"
    componentMgrURN     = "urn:publicid:IDN+geni-in-a-box.net+authority+cm"
    xsiSchemaLocationTag = "xsi:schemaLocation"     # location tag in the main rspec header
    
    
    """\
    Initializes a new instance of GeniManifest.
    
    This constructor expects the request rspec has already
    been parsed and the structure is already set up.
    """
    def __init__(self, users, rspec) :
        self.users = users
        self.rspec = rspec
        self.hosts = experimentHosts
        self.links = experimentLinks
        self.NICs = experimentNICs
        self.validUntil = datetime.datetime.today() +  \
            datetime.timedelta(days = 365)
    
    
    """\
    Retrieves the user names from a users dictionary.
    """
    @classmethod
    def _get_user_names(self, users) :
        
        userNames = [] # the returned list of user names
        
        for user in users :
            userName = None     # the current user the public key is installed for
            # go through every user and get the user's name
            for key in user.keys() :
                # found a user, there should only be one of these per key in 'user'
                if key == "urn" :
                    userName = user[key]
                    userName = userName.split("+")[-1]
            
            # only install the user account if there is a user to install
            if userName != None :
                userNames.append(userName)
    
        return userNames
    
    
    """\
    Creates a manifest rspec file to the given file name.
    """
    def create(self) :
        
        # get the user names that are on the machine for login elements
        userNames = GeniManifest._get_user_names(self.users)
        
        # parse the original document and then set up the children nodes
        originalRspec = parseString(self.rspec).childNodes[0]
        
        # create the document and the main header/wrapper portion
        manifest = Document()
        manifest.appendChild(originalRspec)
        originalRspec.setAttribute(GeniManifest.typeTag, "manifest")
        
        # if the rspec has a xsi:schemaLocation element in the header
        # set the appropriate value to say "manifest" instead of "request"
        if originalRspec.hasAttribute(GeniManifest.xsiSchemaLocationTag) :
            xsiSchemaLocation = originalRspec.attributes[GeniManifest.xsiSchemaLocationTag].value
            xsiSchemaLocation = xsiSchemaLocation.replace("request.xsd", "manifest.xsd")
            originalRspec.setAttribute(GeniManifest.xsiSchemaLocationTag, xsiSchemaLocation)
        
        # if no attribute for xsi:schemaLocation exists then add one
        else :
            originalRspec.setAttribute(GeniManifest.xsiSchemaLocationTag, "xsi:schemaLocation=\"http://www.geni.net/resources/rspec/3 http://www.geni.net/resources/rspec/3/manifest.xsd\"")
        
        # go through every child node within the rspec and
        # set the appropriate values for known node elements
        # and copy over the others that are not known
        for rspecChild in originalRspec.childNodes :

            # skip any test nodes, formatting is taken care
            # of just before the final manifest is written,
            # WARNING: minidom has weird behaviors when text
            # nodes are included, they must be excluded for
            # proper functioning of the xml parser
            if rspecChild.nodeType == rspecChild.TEXT_NODE :
                continue
            
            # if a link element then go through and set the correct values such as ip address and mac addresses
            if rspecChild.nodeName == GeniManifest.linkTag and rspecChild.hasAttribute(GeniManifest.clientIdTag):
                    
                for linkChild in rspecChild.childNodes :
                    
                    if linkChild.nodeType == linkChild.TEXT_NODE :
                        continue
                    
                    # if the child node is a component manager element
                    # then set the name to be geni-in-a-box specific
                    if linkChild.nodeName == GeniManifest.componentManagerTag :
                        linkChild.setAttribute(GeniManifest.nameTag,
                                               GeniManifest.componentMgrURN)
                        
                    # if the child node is an interface reference
                    # then set the appropriate component id
                    elif linkChild.nodeName == GeniManifest.interfaceRefTag and linkChild.hasAttribute(GeniManifest.clientIdTag):
                        # find the NIC object that goes with this interface reference element
                        if linkChild.attributes[GeniManifest.clientIdTag].value in self.NICs.keys() :
                            clientId = linkChild.attributes[GeniManifest.clientIdTag].value
                            componentId = self.NICs[clientId].componentID
                            linkChild.setAttribute(GeniManifest.componentIdTag,
                                                   componentId)
                            sliverID = self.NICs[clientId].sliverURN
                            linkChild.setAttribute(GeniManifest.sliverIdTag, 
                                                   componentId)
                    
            
            # if a node element then go through and set the correct values
            if rspecChild.nodeName == GeniManifest.nodeTag and rspecChild.hasAttribute(GeniManifest.clientIdTag) :
                rspecChild.setAttribute(GeniManifest.exclusiveTag, "false") # no container is exclusive in geni-in-a-box
                
                # find the host object associated with this node
                currentHost = None
                for hostName in self.hosts.keys() :
                    if self.hosts[hostName].nodeName == rspecChild.attributes[GeniManifest.clientIdTag].value :
                        currentHost = self.hosts[hostName]
                        break
                
                # there needs to be a host associated with this node otherwise it is invalid
                if currentHost != None :
                    rspecChild.setAttribute(GeniManifest.clientIdTag,
                                            currentHost.nodeName)
                    rspecChild.setAttribute(GeniManifest.componentManagerIdTag,
                                            GeniManifest.componentMgrURN)

                    rspecChild.setAttribute(GeniManifest.componentIdTag,
                                            currentHost.componentID)
                    rspecChild.setAttribute(GeniManifest.sliverIdTag, 
                                            currentHost.sliverURN)

                    # check if there is a services tag before continuing, there has to be one in order to set login values,
                    # it can't be removed then readded or just appended since it will erase an existing one if it does exist,
                    # which will lose all of the needed information such as installs and downloads
                    hasServicesElement = False
                    for nodeChild in rspecChild.childNodes :
                        if nodeChild.nodeType == nodeChild.TEXT_NODE :
                            continue
                        
                        if nodeChild.nodeName == GeniManifest.servicesTag :
                            hasServicesElement = True
                            break
                    
                    # add the services element if the rspecChild node needs it
                    if not hasServicesElement :
                        servicesElement = manifest.createElement(GeniManifest.servicesTag)
                        rspecChild.appendChild(servicesElement)
                    
                    # add a rs:vnode element then set the correct name with container number
                    rsVnode = manifest.createElement(GeniManifest.rsVnodeTag)
                    rsVnode.setAttribute(GeniManifest.nameTag, 
                                         "pc" + str(currentHost.containerName))
                    rsVnode.setAttribute(GeniManifest.rsnsTag,
                       "http://www.protogeni.net/resources/rspec/ext/emulab/1")

                    rspecChild.appendChild(rsVnode)

                    hostElement = manifest.createElement(GeniManifest.hostTag)
                    hostElement.setAttribute(GeniManifest.nameTag, "pc" +
                                         str(currentHost.containerName) + 
                                         ".geni-in-a-box.net")
                    rspecChild.appendChild(hostElement)
                    
                    # now go through each child element and set the correct values
                    for nodeChild in rspecChild.childNodes :
                        
                        if nodeChild.nodeType == nodeChild.TEXT_NODE :
                            continue
                            
                        # if on a services element then add the login element for each user
                        if nodeChild.nodeName == GeniManifest.servicesTag :
                            for userName in userNames :
                                login = manifest.createElement(GeniManifest.loginTag)
                                login.setAttribute(GeniManifest.authenticationTag, "ssh-keys")
                                login.setAttribute(GeniManifest.hostNameTag,
                                              "pc" + 
                                               str(currentHost.containerName) + 
                                               ".geni-in-a-box.net")
                                login.setAttribute(GeniManifest.portTag, "22") # for now always set to port 22
                                login.setAttribute(GeniManifest.userNameTag, userName)
                                nodeChild.appendChild(login)
                        
                        # if the child node is a sliver type element
                        # then set the correct sliver type
                        elif nodeChild.nodeName == GeniManifest.sliverTypeTag :
                            nodeChild.setAttribute(GeniManifest.nameTag, "virtual-pc")
                            
                            # go through and find the children of the sliver type element,
                            # specifically look for disk images and set the correct type
                            for sliverTypeChild in nodeChild.childNodes :
                                if sliverTypeChild.nodeName == GeniManifest.diskImageTag :
                                    sliverTypeChild.setAttribute(GeniManifest.nameTag, "urn:publicid:geni-in-a-box.net+image+//" + config.distro)
                    
                        # if the child node is an interface
                        # then set up the ip and mac addresses
                        elif nodeChild.nodeName == GeniManifest.interfaceTag :
                            # find the NIC object that goes with this interface element
                            if nodeChild.attributes[GeniManifest.clientIdTag].value in self.NICs.keys() :
                                nic = self.NICs[nodeChild.attributes[GeniManifest.clientIdTag].value]
                            
                                nodeChild.setAttribute(GeniManifest.clientIdTag, nic.nicName)
                                nodeChild.setAttribute(GeniManifest.componentIdTag, nic.componentID)
                                nodeChild.setAttribute(GeniManifest.sliverIdTag,
                                                       nic.sliverURN)
                                nodeChild.setAttribute(GeniManifest.macTag, 
                                                       nic.macAddress)
        
                                # set the ip address, for now this is a sub-element of the
                                # interface element this could also possibly be an attribute
                                ipAddress = manifest.createElement(GeniManifest.ipTag)
                                ipAddress.setAttribute(GeniManifest.addressTag, nic.ipAddress)
                                nodeChild.appendChild(ipAddress)

                        # if a host element then set the correct host name
                        elif nodeChild.nodeName == GeniManifest.hostTag :
                            nodeChild.setAttribute(GeniManifest.nameTag, "pc" +
                                               str(currentHost.containerName) + 
                                               ".geni-in-a-box.net")
        
        # print the rspec to the terminal for display and debugging,
        # this can be removed later on
        manifestXml = manifest.toprettyxml(indent = "  ");
        finalManifest = ""
        
        # clean up some of the spacing that happens from minidom
        for line in manifestXml.split('\n'):
            if line.strip():
                finalManifest += line + '\n'
                
        print finalManifest
        
        # Create the file into which the manifest will be written
        pathToFile = config.sliceSpecificScriptsDir + '/' + config.manifestFile
        try:
            manFile = open(pathToFile, 'w')
        except IOError:
            config.logger.error("Failed to open file that holds manifest: ",
                                pathToFile)
            return None

        manFile.write(finalManifest)
        manFile.close()
        return 0;
