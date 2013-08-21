from openflow.optin_manager.sfa.OFSfaDriver import OFSfaDriver
from openflow.optin_manager.opts.models import Experiment

driver = OFSfaDriver(None)
print '================================='
print 'STARTING SLICE'
print driver.crud_slice('URN:topdomain.subdomain.slice1.urn_more_or_less','topdomain.subdomain',[],'start_slice')
print '================================='
print '\n================================='
print 'STOPPING SLICE'
print driver.crud_slice('URN:topdomain.subdomain.slice1.urn_more_or_less','topdomain.subdomain',[],'stop_slice')
print '================================='
print '\n================================='
print 'REBOOTING SLICE'
print driver.crud_slice('URN:topdomain.subdomain.slice1.urn_more_or_less','topdomain.subdomain',[],'reset_slice')
print '================================='
print '\n================================='
print 'DELETING SLICE'
print driver.crud_slice('URN:topdomain.subdomain.slice1.urn_more_or_less','topdomain.subdomain',[],'delete_slice')
print '================================='

print '\n================================='
print 'Getting deleted slice from experiment model'
print Experiment.objects.get(slice_id='URN:topdomain.subdomain.slice1.urn_more_or_less')
print '==================================='
