import os
from foam.sfa.util.faults import InvalidRSpec, UnsupportedRSpecVersion
from foam.sfa.rspecs.version import RSpecVersion 
#from foam.sfa.util.sfalogging import logger    

class VersionManager:
    def __init__(self):
        self.versions = []
        self.load_versions()

    def load_versions(self):
        path = os.path.dirname(os.path.abspath( __file__ ))
        versions_path = path + os.sep + 'versions'
        versions_module_path = 'foam.sfa.rspecs.versions'
        valid_module = lambda x: os.path.isfile(os.sep.join([versions_path, x])) \
                        and x.endswith('.py') and x !=  '__init__.py'
        files = [f for f in os.listdir(versions_path) if valid_module(f)]
        for filename in files:
            basename = filename.split('.')[0]
            module_path = versions_module_path +'.'+basename
	    try:
            	module = __import__(module_path, fromlist=module_path)
	    except:
		#XXX I do not really understand why the otrer modules works except the OCF module	
	        module = __import__('foam.'+module_path, fromlist='foam.'+module_path)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if hasattr(attr, 'version') and hasattr(attr, 'enabled') and attr.enabled == True:
                    self.versions.append(attr())

    def _get_version(self, type, version_num=None, content_type=None):
        retval = None
        for version in self.versions:
            if type is None or type.lower() == version.type.lower():
                if version_num is None or str(version_num) == version.version:
                    if content_type is None or content_type.lower() == version.content_type.lower() \
                      or version.content_type == '*':
                        retval = version
                        ### sounds like we should be glad with the first match, not the last one
                        break
        if not retval:
	    i = 0
	    for version in self.versions:
		i += 1 
	    #print 'using defaul version:', self.versions[11]
	    #retval = self.versions[9] 
	    #XXX: Both changed due to index error
	    retval = self.versions[0]
	    #XXX: Testing Mode, uncoment the line below when not testing
            #raise UnsupportedRSpecVersion("[%s %s %s] is not suported here"% (type, version_num, content_type))
        return retval

    def get_version(self, version=None):
	print self.versions
        retval = None
        if isinstance(version, dict):
            retval =  self._get_version(version.get('type'), version.get('version'), version.get('content_type'))
        elif isinstance(version, basestring):
            version_parts = version.split(' ')     
            num_parts = len(version_parts)
            type = version_parts[0]
            version_num = None
            content_type = None
            if num_parts > 1:
                version_num = version_parts[1]
            if num_parts > 2:
                content_type = version_parts[2]
            retval = self._get_version(type, version_num, content_type) 
        elif isinstance(version, RSpecVersion):
            retval = version
        else:
            raise UnsupportedRSpecVersion("No such version: %s "% str(version))
 
        return retval

    def get_version_by_schema(self, schema):
        retval = None
        for version in self.versions:
            if schema == version.schema:
                retval = version
        if not retval:
            raise InvalidRSpec("Unkwnown RSpec schema: %s" % schema)
        return retval

def show_by_string(string):
    try:
        print v.get_version(string)
    except Exception,e:
        print e
def show_by_schema(string):
    try:
        print v.get_version_by_schema(string)
    except Exception,e:
        print e

if __name__ == '__main__':
    v = VersionManager()
    print v.versions
    show_by_string('sfa 1') 
    show_by_string('protogeni 2') 
    show_by_string('protogeni 2 advertisement') 
    show_by_schema('http://www.protogeni.net/resources/rspec/2/ad.xsd') 
    show_by_schema('http://sorch.netmode.ntua.gr/ws/RSpec/ad.xsd')

