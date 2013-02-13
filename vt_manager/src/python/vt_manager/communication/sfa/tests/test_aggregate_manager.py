from vt_manager.communication.sfa.AggregateManager import AggregateManager
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

options = Options(123456)
agg = AggregateManager(None)
print 'Aggregate instance:',agg
xml = agg.ListResources(None,None,options)
print '------------------ListResources:',xml

#XXX: Last test was 02/13/2013 with OK results, the first temptative of OCF rspecs are done(based in PGv2). OCF Rspecs need to be improved and clearify the XRN, HRN and URN concepts in order to offer the correct notation for aggregates, component managers, slices etc. 
