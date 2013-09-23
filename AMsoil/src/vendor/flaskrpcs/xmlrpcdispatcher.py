import os.path
from flask import request

from amsoil.core import serviceinterface
import amsoil.core.pluginmanager as pm

from amsoil.config import expand_amsoil_path

import exceptions

class XMLRPCDispatcher(object):
    """Please see documentation in FlaskXMLRPC."""
    @serviceinterface
    def __init__(self, log):
        self._log = log

    @serviceinterface
    def requestCertificate(self):
        """Retrieve the certificate which the client has sent. If using the development server, the certificate can not be determined (werkzeug is stupid in that sense)."""
        # get it from the request's environment
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
