import sys

from sfa.trust.auth import Auth
from sfa.util.faults import InsufficientRights, MissingCallerGID, MissingTrustedRoots, PermissionError, \
    BadRequestHash, ConnectionKeyGIDMismatch, SfaPermissionDenied


#Check if the given Credentials have rights on the aggregate

class AuthManager:

    def checkCredentials(self, creds, operation, hrn=None):
	Auth.checkCredentials(creds, operation, hrn)
