from vt_manager.communication.sfa.AggregateManager import AggregateManager
'''
This module run tests over the AM locally without xmlrpc or sfa instances
'''

class Options:

	def __init__(self,callId='fancy-UUID',sliceId=None):
		self.call_id = callId
		self.geni_slice_urn = None
		self.geni_rspec_version = 'pgv2'

	def get(self,attr,extra=None):
		return getattr(options,attr)

options = Options(123456)
agg = AggregateManager(None)
print 'Aggregate instance:',agg
xml = agg.ListResources(None,None,options)
print '------------------ListResources:',xml

#XXX: Last test was 02/08/2013 with OK results, but uncomplete RSpec( Still missing OS,Virtualization, State, Name, etc. from servers)
