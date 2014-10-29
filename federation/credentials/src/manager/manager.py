from ambase.src.abstract.classes.credentialmanagerbase import CredentialManagerBase
from credentials.src.trust.auth import Auth
from credentials.src.trust.credential import Credential
from credentials.src.trust.abaccredential import ABACCredential
from ambase.src.ambase.exceptions import ApiErrorException
from ambase.src.geni.exceptions.manager import GENIExceptionManager

class CredentialManager(CredentialManagerBase):
    
    def __init__(self):
        self.__config = None
        self.__auth = None#Auth()
        
    def get_auth(self):
        return self.__auth

    def set_auth(self, value):
        self.__auth = value

    def validate_for(self, method, credentials):
        return self._get_geniv2_validation(method, credentials)
        
    def get_valid_creds(self):
        return ""

    def get_expiration_list(selfi, credentials):
        expirations = list()
        for cred in credentials:
            expirations.append(cred.expiration)
        return expirations

    def get_slice_expiration(self, credentials):
        
        return  ""

    def __clean_credentials(self, credentials):
        clean_creds = [c['geni_value'] for c in filter(self.__is_geni_cred, credentials)]
        return clean_creds

    def _get_geniv2_validation(self, method, credentials):
        method = self._translate_to_geniv2_method(method)
        try:
            if self.__auth == None:
                self.__auth = Auth(config=self.__config)
            credentials = self.__clean_credentials(credentials)#[c['geni_value'] for c in filter(self.__is_geni_cred, credentials)]
            valid_cred = self.__auth.checkCredentials(credentials, method)
        except Exception as e:
            raise e
    
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
        raise Exception("Unknown method: %s" % method)
    
    def __is_geni_cred(self, credential):
        """
        Filter (for use with filter()) to yield all 'geni_sfa' credentials
        regardless over version.
        """
        if not isinstance(credential, dict):
            msg = "Bad Arguments: Received credential of unknown type %r"
            msg = msg % (type(credential))
            raise ApiErrorException(GENIExceptionManager.BADARGS, msg)
        return ('geni_type' in credential
                and str(credential['geni_type']).lower() in [Credential.SFA_CREDENTIAL_TYPE,
                                                       ABACCredential.ABAC_CREDENTIAL_TYPE])

    def get_config(self):
        return self.__config
    
    def set_config(self, value):
        self.__config = value 
