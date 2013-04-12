from openflow.optin_manager.sfa.OFSfaDriver import OFSfaDriver
from openflow.optin_manager.sfa.sliver_example import rspec
driver = OFSfaDriver(None)

print driver.create_sliver('slice1','topdomain.subdomain',rspec,[],{})

