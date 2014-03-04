#----------------------------------------------------------------------
# Copyright (c) 2011 Raytheon BBN Technologies
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

from resource import Resource

class Aggregate(object):

    def __init__(self):
        self.resources = []
        self.containers = {}

    def add_resources(self, resources):
        self.resources.extend(resources)

    def catalog(self, container=None):
        if container:
            if container in self.containers:
                return self.containers[container]
            else:
                return []
        else:
            return self.resources

    def allocate(self, container, resources):
        if container not in self.containers:
            self.containers[container] = []
        for r in resources:
            self.containers[container].append(r)

    def deallocate(self, container, resources):
        if container and not self.containers.has_key(container):
            # Be flexible: if a container is specified but unknown
            # ignore the call
            return
        if container and resources:
            # deallocate the given resources from the container
            for r in resources:
                self.containers[container].remove(r)
        elif container:
            # deallocate all the resources in the container
            for r in self.containers[container]:
                self.containers[container].remove(r)
        elif resources:
            # deallocate the resources from their container
            for r in resources:
                for c in self.containers.values():
                    if r in c:
                        c.remove(r)
        # Finally, check if container is empty. If so, delete it.
        # Note cache the keys because we will be modifying the dict
        # inside the loop
        allkeys = self.containers.keys()
        for k in allkeys:
            if not self.containers[k]:
                del self.containers[k]

    def stop(self, container):
        # Mark the resources as 'SHUTDOWN'
        if container in self.containers:
            for r in self.containers[container]:
                r.status = Resource.STATUS_SHUTDOWN
