import unittest
from credentials.src.test.utils.chcalls import getusercred
from credentials.src.manager.gcfmanager import GCFCredentialManager
from settings.src.settings import Settings
from credentials.src.trustgcf.cred_util import CredentialVerifier



class TestCredentials(unittest.TestCase):
    
    def setUp(self):
        self.trusted_roots = Settings.TRUSTED_ROOTS_DIR
        self.credential_verifier = CredentialVerifier(self.trusted_roots)
        self.cred = getusercred()[1]['geni_value']
        self.own_gid_string = '''-----BEGIN CERTIFICATE-----
MIICFDCCAX2gAwIBAgIBAzANBgkqhkiG9w0BAQQFADAUMRIwEAYDVQQDEwl0b3Bk
b21haW4wHhcNMTIxMjI3MDgwNDEyWhcNMTcxMjI2MDgwNDEyWjAUMRIwEAYDVQQD
Ewl0b3Bkb21haW4wgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBAO+j5DIFYJhA
jyB+2VtipZhFIx/bcGOa35vOEZfagKsaaIgdelBZwyALG99yB3pLvDF8wprO16Je
KODSBhN/VjF0QM2CKpSOJXQvvpeWeTXFEhOUA0N6xkCLyzMwe0tchXlKZRPLXhBu
WaWgt9E1rOEYAkCro5tx1e98SlH9wQM3AgMBAAGjdjB0MA8GA1UdEwEB/wQFMAMB
Af8wYQYDVR0RBFowWIYndXJuOnB1YmxpY2lkOklETit0b3Bkb21haW4rYXV0aG9y
aXR5K3Nhhi11cm46dXVpZDpjN2RmZDU5Yy1jOTNjLTRmZDUtOWQ1My03MzQ1MDQw
NDcwODMwDQYJKoZIhvcNAQEEBQADgYEAHCjfsJt348ew4JQorY98gCjMVadJg/wn
0HJie1RrJl0nxxaY6u71SZ7AxXCAvKWcqFzQ7vvP/mgrWhZmCo018xj9tPvdKKAs
UePmSIEjb1zcmW5hrWqNKAlBG7KjNJ23iaK4F/9Zhyih9jYqXAFsysH5g1KnI9T3
JK9yxZ7Nytw=
-----END CERTIFICATE-----'''

    def test_should_check_correct_credential(self):
        creds = self.credential_verifier.verify_from_strings(self.own_gid_string, [self.cred], None,["listnodes"], {})
        print creds
       # print creds[0].expiration
        print creds[0].get_gid_caller().get_hrn()
        print creds[0].get_gid_caller().get_pubkey().get_pubkey_string()
        
        