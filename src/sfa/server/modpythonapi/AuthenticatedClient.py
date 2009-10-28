from sfa.trust.certificate import Keypair
from sfa.trust.gid import GID

from BaseClient import BaseClient

class AuthenticatedClient(BaseClient):
    def __init__(self, url, private_key_file, gid_file=None, cred_file=None):
        BaseClient.__init__(self, url)
        self.private_key_file = private_key_file
        self.gid_file = gid_file
        self.cred_file = cred_file
        self.private_key = Keypair(filename = self.private_key_file)
        if gid_file:
            self.gid = GID(filename = self.gid_file)
        if cred_file:
            self.cred = Credential(filename = self.cred_file)

    def computeRequestHash(self, argList):
        return self.private_key.sign_string(str(argList))

    def gidNoop(self, value):
        gidStr = self.gid.save_to_string(True)
        reqHash = self.computeRequestHash([gidStr, value])
        return self.server.gidNoop(gidStr, value, reqHash)
