from openflow.optin_manager.sfa.OFSfaDriver import OFSfaDriver

driver = OFSfaDriver(None)

print driver.sliver_status('URN:topdomain.subdomain.slice1.urn_more_or_less','topdomain.subdomain',[],{})
