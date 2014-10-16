from ambase.src.abstract.classes.credentialmanagerbase import CredentialManagerBase

class MockCredentialManager(CredentialManagerBase):
    
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

    def get_slice_expiration(self, credentials):
        import datetime
        import dateutil.parser
        current_date = datetime.datetime.utcnow()
        six_months = datetime.timedelta(weeks = 6 * 4) # 6 months
        slice_expiration = current_date + six_months
        try:
            slice_expiration.replace(tzinfo=dateutil.tz.tzutc()).strftime("%Y-%m-%d %H:%M:%S").replace(" ", "T")+"Z"
        except:
            pass
        return slice_expiration

