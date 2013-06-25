from openflow.optin_manager.sfa.trust.hierarchy import Hierarchy


def create_authority(xrn, subject=None):
    #xrn = 'ocf.i2cat.ofam'
    create_parents = False
    #subject = {'CN':'ca.i2cat.fp7-ofelia.eu', 'C':'SP','ST':'Catalunya', 'L':'Barcelona','O':'i2CAT','OU':'DANA'}
    hierarchy = Hierarchy()
    #Create auth with parents
    hierarchy.create_auth(xrn,create_parents)

