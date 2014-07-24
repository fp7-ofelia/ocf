from src.abstract.classes.credentialmanager import CredentialManager

class MockCredentialManager(CredentialManager):
    
    def __init__(self, success_mode = True):
        self.success_mode = success_mode
    
    def verify_credential_for(self, credentials=list(), method=None):
        if self.success_mode:
            return True
        else:
            raise Exception("Credential verification failed")
    
    