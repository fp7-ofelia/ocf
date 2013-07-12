from exception import *

class Signal (object):
    '''
    Wrapps a Blinker Signal resulting in a unicast/multicast enabled
    signal. Instances of it are returned by the Notification Center 
    to the plugin, module, etc which asks for them. 
    Interface calls which are oficially supported by AMsoil are:
    enableMulticast()
    disableMulticast()
    send()
    connect()
    resolvers
    '''
    def __init__(self, signal):
        self._wrapped_sig = signal
        self._unicast = False
 

    def __getattr__(self, attr):
        if attr == "connect":
            if len(self._wrapped_sig.receivers) >=1 and self._unicast:
                raise TooManySignalConsumers(self)
 
        if attr in self.__dict__:
            return getattr(self, attr)
 
        return getattr(self._wrapped_sig, attr)

    def disableMulticast(self):
        if len(self._wrapped_sig.receivers) > 1:
            raise TooManySignalConsumers(self)
        self._unicast = True
