#----------------------------------------------------------------------
# Copyright (c) 2010 Raytheon BBN Technologies
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
import json

class OmniSpec(dict):
    """
    An omnispec is meant to be an intermediate representation of RSpecs from various aggregates.
    The omnispec representation can then be used by tools to present resources to users, in an 
    rspec-format agnostic way.  Once the user has selected the resources that they want, the
    omnispecs are then reverted back into aggregate-specific formats and sent back to the 
    aggregates to create the slivers.
    
    An omnispec instance represents a conversion of an rspec from a single aggregate.  The type and urn
    of the aggregate are stored in the omnispec so that it can be reverted later.  Each resource represented
    in the rspec is converted into an OmniResource, and the omnispec keeps a list of OmniResources.
    """
    def __init__(self, type, urn, filename = None, dictionary = None):
        # URN is that of the AM whose resources these are
        dict.__init__(self, {})    

        if filename:
            self.from_json_file(filename)
        elif dictionary:
            self.from_dict(dictionary)
        else:            
            self['type'] = type
            self['urn'] = urn
            self['resources'] = {}
        
    def add_resource(self, urn, resource):
        self['resources'][urn] = resource

    def get_resources(self):
        return self.get('resources')
    def get_type(self):
        return self.get('type')
    
    def __str__(self):
        return self.to_json()
    
    def to_json(self):
        return json.dumps(self, indent=4)
    
        
    def from_dict(self, dictionary):
        self.update(dictionary)
        updates = {}
        for u, r in self['resources'].items():
            updates[u] = OmniResource('','','',dictionary=r)
        for u, r in updates.items():
            self['resources'][u] = r
            
    def from_json_file(self, filename):
        string = file(filename,'r').read()
        return self.from_json(self, string)
    

class OmniResource(dict):
    """
    An omniresource is an intermediate representation of a single resource in an rspec.
    Its fields are very general, such as the type of the resource, and the name of the resources.
    Descriptive information that should be presented to the user can be set in the description.
    Options that the user can specify, such as memory usage, bandwidth, vlans, etc.. should be stored
    in the options dictionary.  Specific information about the resource that is needed to reconstruct
    the RSpec from the OmniResource should be placed in the misc dictionary.
    
    Field descriptions:
    Name: The name of the resource
    Description: Details about the resource that the user might want to read
    Type: Is it a link? a vm? a switch?
    Allocated: Is this resource currently allocated?
    Allocate: This is set to true by the user if they want to allocate this resource in CreateSliver
    Options: Settings that the user can adjust
    Misc: Extra information mainly meant for conversion back from omnispec to rspecs
    
    Future ideas:
    Should probably add location information for each resource.
    """
    def __init__(self, name, description, type, dictionary=None):
        dict.__init__(self, {})
        if dictionary:
            self.update(dictionary)
        else:
            self.set_name(name)
            self.set_description(description)
            self.set_type(type)
            self['options'] = {}
            self['allocated'] = False
            self['allocate'] = False
            self['misc'] = {}
        
    def set_name(self, name):
        self['name'] = name
    def get_name(self):
        return self['name']
    def set_description(self, description):
        self['description'] = description
    def get_description(self):
        return self['description']
    def set_type(self, type):
        self['type'] = type
    def get_type(self):
        return self['type']
    
    def add_option(self, name, defValue=None):
        if not defValue:
            defValue = ''
        self['options'][name] = defValue
    def set_allocated(self, value):
        self['allocated'] = value
    def get_allocated(self):
        return self['allocated']
    def get_allocate(self):
        return self['allocate']
    
    def get_misc(self):
        return self['misc']
    
    def __str__(self):
        return self.to_json()
    
    def to_json(self):
        return json.dumps(self, indent=4)
        
