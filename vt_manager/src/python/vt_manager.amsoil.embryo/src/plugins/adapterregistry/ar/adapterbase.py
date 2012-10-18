import abc

from amsoil.core import serviceinterface

class AdapterBase(object):

    __metaclass__ = abc.ABCMeta

    @serviceinterface
    def supportsType(self, theType):
        """
        Returns if this object does support the given type.
        The default implementation checks if this type is a subclass of the_type.
        Please override if you need to do fancy stuff
        """
        return issubclass(self.__class__, theType)
        