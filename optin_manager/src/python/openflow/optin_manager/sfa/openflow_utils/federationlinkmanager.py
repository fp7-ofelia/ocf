from openflow.optin_manager.sfa.sfa_config import config

class FederationLinkManager:
    @staticmethod
    def get_federated_links():
        return config.FEDERATED_LINKS
