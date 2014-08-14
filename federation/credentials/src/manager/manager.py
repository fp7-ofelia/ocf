from ambase.src.abstract.classes.credentialmanagerbase import CredentialManagerBase
from credentials.src.trust.auth import Auth

class CredentialManager(CredentialManagerBase):
    
    def __init__(self):
        self.__auth = Auth()

    def get_auth(self):
        return self.__auth

    def set_auth(self, value):
        self.__auth = value

    def validate_for(self, credentials, method):
        return self._get_geniv2_validation(method, credentials)
        
    def get_valid_creds(self):
        return ""

    def get_expiration_list(self):
        return ""
    
    def _get_geniv2_validation(self, method, credentials):
        method = self._translate_to_geniv2_method(method)
        valid_creds = self.__auth.checkCredentials(credentials, method)
        return 
    
    def _translate_to_geniv2_method(self, method):
        if method == "Allocate" or method == "Provision":
            return "createsliver"
        elif method == "ListResources":
            return "listnodes"
        elif method == "Describe" or method == "Status":
            return "sliverstatus"
        elif method == "PerforOperationalAction":
            return "startslice"
        elif method == "Delete":
            return "deletesliver"
        elif method == "Renew":
            return "renewsliver"
        raise Exception("Unknown method")
    
