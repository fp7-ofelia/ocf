import threading

from amsoil.core import serviceinterface

from cs.exceptions import NoCurrentContextAvailableError

localstore = threading.local()

class ContextStorage(object):
    @serviceinterface
    def __init__(self, user_id, rpc_type, rpc_version):
        """
        Initialize the context and append this object to the thread's local storage.
        This context is thread local because it shall be unique for each request.
        The saving to thread local might override an old context object, but that is ok because the context is supposed to represent the current request.
        So if there is a new request it actually should overwrite the old object.
        
        This module should also work in a pre-fork environment, because the thread local storage also is unique then.
        """
        self._user_id = user_id
        self._rpc_type = rpc_type
        self._rpc_version = rpc_version
        self._data = {}
        localstore.amcontext = self

    @classmethod
    @serviceinterface
    def currentContext(klass):
        """Get the current context."""
        try:
            res = localstore.amcontext
        except AttributeError:
            raise NoCurrentContextAvailableError()
        return res

    @property
    @serviceinterface
    def user_id(self):
        return self._user_id
    @property
    @serviceinterface
    def rpc_type(self):
        return self._rpc_type
    @property
    @serviceinterface
    def rpc_version(self):
        return self._rpc_version

    @property
    @serviceinterface
    def data(self):
        return self._data
    # def __getitem__(self, key):
    #     return self._info[key]
    #     
    # def __setitem__(self, key, value):
    #     self._info[key] = value
    #     
    # def __contains__(self, key):
    #     return self._info.__contains__(key)
