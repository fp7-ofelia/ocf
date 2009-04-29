from soaplib.wsgi_soap import SimpleWSGISoapApp
from soaplib.service import soapmethod
from soaplib.serializers.primitive import *
from soaplib.serializers.clazz import *
#import cElementTree as et
from geniLight_types import *

##
# The GeniServer class provides stubs for executing Geni operations at
# the Aggregate Manager.

class GeniResult(ClassSerializer):
	class types:
		code = Integer
		error_msg = String

class GeniLightServer(SimpleWSGISoapApp):
    	# implicitly no __init__()
    @soapmethod(UserSliceInfo,_returns=GeniResult)
    def start_slice(self, slice):
    	g = GeniResult()
	g.code=1
	g.error_msg = 'Success'
        return g

    @soapmethod(UserSliceInfo,_returns=GeniResult)
    def stop_slice(self, slice):
        return GeniResult(1, 'Success')

    @soapmethod(UserSliceInfo,_returns=GeniResult)
    def delete_slice(self, slice):
        return GeniResult(1, 'Success')

    @soapmethod(UserSliceInfo,String,_returns=GeniResult)
    def create_slice(self, slice, rspec_str):
        return GeniResult(1, 'Success')

    @soapmethod(_returns=String)
    def list_slices(self):
        return 'list of slices'

    @soapmethod(_returns=String)
    def list_components(self):
        return 'list of components'

    @soapmethod(GeniRecordEntry,_returns=GeniResult)
    def register(self, record):
        return GeniResult(1, 'Success')

    @soapmethod(String,_returns=GeniResult)
    def reboot_component(self,name):
        return GeniResult(1, 'Success')

if __name__=='__main__':
    try:from cherrypy.wsgiserver import CherryPyWSGIServer
    except:from cherrypy._cpwsgiserver import CherryPyWSGIServer
    server = CherryPyWSGIServer(('localhost',7889),GeniLightServer())
    server.start()

