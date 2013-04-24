from openflow.optin_manager.sfa.OFSfaDriver import OFSfaDriver

driver = OFSfaDriver(None)

print driver.list_resources('URN:topdomain.subdomain.slice1.urn_more_or_less',None,[],{})
