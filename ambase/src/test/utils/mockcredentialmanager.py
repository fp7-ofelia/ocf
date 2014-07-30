from src.abstract.classes.credentialmanager import CredentialManager

class MockCredentialManager(CredentialManager):
    
    def __init__(self, success_mode = True):
        self.success_mode = success_mode
    
    def validate_for(self, credentials=list(), method=None):
        if self.success_mode:
            return True
        else:
            raise Exception("Credential verification failed")

    def get_valid_creds(self):
        return []
    
    def get_expiration_list(self):
        return []    
    