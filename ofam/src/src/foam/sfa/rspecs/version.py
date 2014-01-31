#!/usr/bin/python
#from foam.sfa.util.sfalogging import logger

class RSpecVersion:
    type = None
    content_type = None
    version = None
    schema = None
    namespace = None
    extensions = {}
    namespaces = dict(extensions.items() + [('default', namespace)])
    elements = []
    enabled = False

    def __init__(self, xml=None):
        self.xml = xml

    def to_dict(self):
        return {
            'type': self.type,
            'version': self.version,
            'schema': self.schema,
            'namespace': self.namespace,
            'extensions': self.extensions.values()
        }

    def __str__(self):
        return "%s %s" % (self.type, self.version)
    

