import sys
from os.path import dirname, join, normpath
PYTHON_DIR = normpath(join(dirname(__file__), '../../'))
sys.path.insert(0,PYTHON_DIR)

from amsoil.core.exception import CoreException

class TooManySignalConsumers(CoreException):
    '''
    TooManySignalConsumers
    '''
    def __init__ (self, signal):
        super(TooManySignalConsumers, self).__init__()
        self._signal= signal

    def __str__ (self):
        return "Signal %r can not handle more than 1 receiver since it is unicast" % self._signal


