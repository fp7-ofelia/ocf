from openflow.optin_manager.sfa.trust.hierarchy import Hierarchy

xrn = 'ocf.i2cat.ofam'
create_parents = True
subject = {'CN':'OfeliaSDKR1', 'C':'SP','ST':'Catalunya', 'L':'Barcelona','O':'i2CAT','OU':'DANA'}
hierarchy = Hierarchy()
#Create auth with parents
hierarchy.create_auth(xrn,create_parents,subject)

