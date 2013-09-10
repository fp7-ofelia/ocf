from openflow.optin_manager.sfa.OFSfaDriver import OFSfaDriver
from openflow.optin_manager.sfa.sliver_example import rspec
driver = OFSfaDriver(None)

print driver.create_sliver('URN:topdomain.subdomain.slice1.urn_more_or_less','topdomain.subdomain',rspec,[],{})

