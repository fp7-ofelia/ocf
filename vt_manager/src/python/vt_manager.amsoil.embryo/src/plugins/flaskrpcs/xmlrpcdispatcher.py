from flask import request

from amsoil.core import serviceinterface

import exceptions

class XMLRPCDispatcher(object):
    """Please see documentation in FlaskXMLRPC."""
    @serviceinterface
    def __init__(self, log):
        self._log = log

    @serviceinterface
    def requestCertificate(self):
        if request.environ.has_key('CLIENT_RAW_CERT'):
            return request.environ['CLIENT_RAW_CERT']
        return None
        

    def _dispatch(self, method, params):
        self._log.info("Called: <%s>" % (method))
        try:
            meth = getattr(self, "%s" % (method))
        except AttributeError, e:
            self._log.warning("Client called unknown method: <%s>" % (method))
            raise e

        try:
            return meth(*params)
        except Exception, e:
            # TODO check if the exception has already been logged
            self._log.exception("Call to known method <%s> failed!" % (method))
            raise e
