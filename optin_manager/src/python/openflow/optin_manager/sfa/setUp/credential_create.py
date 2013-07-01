from openflow.optin_manager.sfa.managers.MetaSfaRegistry import MetaSfaRegistry

def create_credential(xrn):
    MetaSfaRegistry().get_credential(xrn)

