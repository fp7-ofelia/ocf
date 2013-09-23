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

import logging
import os
import subprocess

import resources
import rspec_handler
import config

# GENI-in-a-box specific createSliver
def createSliver(slice_urn, requestRspec, users) :
    """
        Create a sliver on this aggregate.
    """
    config.logger.info("createSliver called")

    # Parse the request rspec
    rspec_handler.parseRequestRspec(slice_urn, requestRspec)

    # Provision the sliver i.e. assign resource as specifed in the request rspec
    #    The sliver isn't created yet.  The shell commands used to create
    #    the sliver are written into the file named in config.py
    resources.provisionSliver(users)

    # Generate the manifest rspec.  The manifest is written to the file named
    #    in config.py
    (rspec_handler.GeniManifest(users, requestRspec)).create()

    # Add commands to the bash script that create special files/directories
    #    in the containers.  They contain slice configuration information
    #    such as manifest rspec, slice name, etc.
    resources.specialFiles()

    ## Execute the shell script that create a new sliver
    pathToFile = config.sliceSpecificScriptsDir + '/' + config.shellScriptFile
    command = 'echo \"%s\" | sudo -S %s' % (config.rootPwd, pathToFile)
    print command
    os.system(command)


def deleteSliver() :
    """
       Delete the sliver created on this aggregate.
    """
    config.logger.info("createSliver called")

    # Invoke the deleteSliver script in the standardScipts directory
    pathToFile = config.standardScriptsDir + '/' + config.deleteSliver
    command = 'echo \"%s\" | sudo -S %s %s %s' % (config.rootPwd,
                                                  pathToFile,
                                                  config.homeDirectory,
                                                  config.sliceSpecificScriptsDir
                                               )
    print command
    os.system(command)

    # Delete the file containing the manifest rspec
    pathToFile = config.sliceSpecificScriptsDir + '/' + config.manifestFile
    os.remove(pathToFile)
    
    # Free up internal data structures representing these resources
    resources.freeResources()


def sliverStatus(slice_urn) :
    """
        Return the status of the resources that belong to this sliver.
    """
    config.logger.info("sliverStatus called")

    # Get a list of statuses for each of the VM resources
    resourceStatusList = resources.getResourceStatus()

    # Determine the overall status of the slice at this aggregate
    #     If any resource is 'shutdown', the sliver is 'shutdown'
    #     else if any resource is 'failed', the sliver is 'failed'
    #     else if any resource is 'configuring', the sliver is 'configuring'
    #     else if all resources are 'ready', the sliver is 'ready'
    #     else the sliver is 'unknown'
    
    # Make a list that contains the status of all resources
    statusList = list()
    for i in range(len(resourceStatusList)) :
        statusList.append(resourceStatusList[i]['geni_status'])

    sliceStatus = 'unknown'
    if 'shutdown' in statusList :
        sliceStatus = 'shutdown'
    elif 'failed' in statusList :
        sliceStatus = 'failed'
    elif 'configuring' in statusList :
        sliceStatus = 'configuring'
    elif 'ready' in statusList :
        # Count number of resources that are ready.  If all resources are
        #    ready, the slice is ready.
        readyCount = 0;
        for i in range(len(resourceStatusList)) :
            if resourceStatusList[i]['geni_status'] == 'ready' :
                readyCount += 1
        print '%s resources are ready\n' % readyCount
        if readyCount == len(resourceStatusList) :
            sliceStatus = 'ready'

    return dict(geni_urn = resources.sliceURN, \
                    geni_status = sliceStatus, \
                    geni_resources = resourceStatusList)
    


def get_manifest() :
    """
        Return the manifest rspec for the current slice.  The manifest
        is in a file created by rspec_handler.GeniManifest.
    """
    pathToFile = config.sliceSpecificScriptsDir + '/' + config.manifestFile
    config.logger.info('Reading manifest from %s' % pathToFile)
    try:
        f = open(pathToFile, 'r')
    except IOError:
        config.logger.error("Failed to open manifest rspec file %s" % 
                            pathToFile)
        return None

    manifest = f.read()
    f.close()
    return manifest


def get_advert() :
    """
         Return the advertisement rspect for this aggregate.  Get this manifest
         from a pre-created, static file.
    """
    pathToFile = config.standardScriptsDir + '/' +  config.advertRspecFile
    config.logger.info('Reading advert rspec from %s' % pathToFile)
    try:
        f = open(pathToFile, 'r')
    except IOError:
        config.logger.error("Failed to open advertisement rspec file %s" %
                             pathToFile)
        return None

    advert = f.read()
    f.close()

    return advert
    
