from vt_manager.communication.sfa.AggregateManager import AggregateManager
from vt_manager.communication.sfa.tests.example_vm_rspec import rspec as RSPEC
from vt_manager.communication.utils.XmlHelper import *
from vt_manager.controller.dispatchers.xmlrpc.ProvisioningResponseDispatcher import ProvisioningResponseDispatcher as prd
from vt_manager.utils.ServiceThread import *
from vt_manager.communication.sfa.tests.hardcoded_vars import users as USERS
'''
This module run tests over the AM locally without xmlrpc or sfa instances
'''


class Options:

	def __init__(self,callId='fancy-UUID',sliceId=None):
		self.call_id = callId
		self.geni_slice_urn = None
		self.geni_rspec_version = 'OcfVt'

	def get(self,attr,extra=None):
		return getattr(options,attr)

xrn = 'urn:publicid:IDN+topdomain:nitos+slice+SFATest'
users = USERS
options = Options(123456)
agg = AggregateManager(None)
print 'Aggregate instance:',agg
xml = agg.ListResources(None,None,options)
#print '------------------ListResources:',xml
#options.geni_slice_urn = 'slice-name'
#print 'Second List Resources'
#xml = agg.ListResources(None,None,options)
#print '-----------------ListResources with slice parametre:', xml

#XXX: Last ListResources() test was 02/13/2013 with OK results, the first temptative of OCF rspecs are done(based in PGv2). OCF Rspecs need to be improved and clearify the XRN, HRN and URN concepts in order to offer the correct notation for aggregates, component managers, slices etc. 
#
#xml = agg.CreateSliver(None, xrn, None, RSPEC, users, None)
#print xml
#XXX: Last CreateSliver() test was 02/25/2013 with OK results. The test does not get any parametre from VTShell yet, but the RSpec parsing(v1) is OK. The CreateSliver and GetSlice VTShell functions should be implemented working with slice_leaf parametre in order to check the manifest response RSpec.

#xml = agg.stop_slice(None,xrn,None)
#xml = agg.reset_slice(None,xrn)
#xml = agg.SliverStatus(None,xrn,None,None)
#xml = agg.DeleteSliver(None,xrn,None,None)
print xml


