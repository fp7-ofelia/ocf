import sys
from os.path import dirname, join, normpath
PYTHON_DIR = normpath(join(dirname(__file__), '../../'))
sys.path.insert(0,PYTHON_DIR)

from amsoil.core.exception import CoreException

class PolicyError(CoreException):
    '''
    General PolicyError
    '''
    def __init__ (self):
        super(PolicyError, self).__init__()
    
    def __str__ (self):
        return "Policy Manager Plugin Error"


class UnexistingPolicyError(CoreException):
    '''
    UnexistingPolicyError
    '''
    def __init__ (self, scopeName):
        super(UnexistingPolicyError, self).__init__()
        self._scope = scopeName

    def __str__ (self):
        return "The Policy Manager Plugin has not defined a Policy scope called %s", self._scope


class PolicyNotFulfilledError(CoreException):
    '''
    PolicyNotPassedError
    '''
    def __init__ (self, scopeName):
        super(PolicyNotFulfilledError, self).__init__()
        self._scope = scopeName

    def __str__ (self):
        return "Request has not fulfilled the rules defined in the Policy scope %s", self._scope
