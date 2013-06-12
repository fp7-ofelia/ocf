from openflow.optin_manager.sfa.MetaSfaRegistry import MetaSfaRegistry

def create_credential(xrn):
    MetaSfaRegistry().get_credential(xrn)

