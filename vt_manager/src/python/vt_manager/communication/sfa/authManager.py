import sys

from vt_manager.communication.sfa.trust.auth import Auth
from vt_manager.communication.sfa.util.faults import InsufficientRights, MissingCallerGID, MissingTrustedRoots, PermissionError, BadRequestHash, ConnectionKeyGIDMismatch, SfaPermissionDenied


#Check if the given Credentials have rights on the aggregate

class AuthManager:

    def checkCredentials(self, creds, operation, hrn=None):
	result = Auth.checkCredentials(creds, operation, hrn)
	return result
