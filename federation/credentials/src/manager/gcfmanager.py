from ambase.src.abstract.classes.credentialmanagerbase import CredentialManagerBase
from credentials.src.trustgcf.cred_util import CredentialVerifier

class GCFCredentialManager(CredentialManagerBase):
    
    def __init__(self):
        self.__config = None
        self.__root_cert = None
        self.__auth = None#CredentialVerifier()
        
    def get_auth(self):
        return self.__auth
    
    def get_config(self):
        return self.__config
    
    def get_root_cert(self):
        return self.__root_cert

    def set_auth(self, value):
        self.__auth = value
        
    def set_config(self, value):
        self.__config = value
        root_cert = open(self.__config.ROOT_CERT, 'r').read()
        self.__root_cert = root_cert
        self.__auth = CredentialVerifier(self.__config.TRUSTED_ROOTS_DIR)
        
    def set_root_cert(self,value):
        self.__root_cert = value

    def validate_for(self,  method, credentials):
        credentials = self.__clean_credentials(credentials)
        return self._get_geniv2_validation(method, credentials)
        
    def get_valid_creds(self):
        return ""

    def get_expiration_list(self, credentials):
        expirations = list()
        for cred in credentials:
            expirations.append(cred.expiration)
        return expirations

    def get_slice_expiration(self, credentials):
        return credentials[0].expiration

    def _get_geniv2_validation(self, method, credentials):
        method = (self._translate_to_geniv2_method(method),)
        try:
            valid_cred = self.__auth.verify_from_strings(self.__root_cert,credentials,None, method, {})
            return valid_cred
        except Exception as e:
            raise e
    
    def _translate_to_geniv2_method(self, method):
        if method == "Allocate" or method == "Provision":
            return "createsliver"
        elif method == "ListResources":
            return "listnodes"
        elif method == "Describe" or method == "Status":
            return "sliverstatus"
        elif method == "PerformOperationalAction":
            return "createsliver"
        elif method == "Delete":
            return "deletesliver"
        elif method == "Renew":
            return "renewsliver"
        raise Exception("Unknown method %s", method)

    def __clean_credentials(self, credentials):
        creds = list()
        for cred  in credentials:
            if cred.get("geni_value"):
                creds.append(cred["geni_value"])
            else: 
                creds.append(cred)
        return creds
