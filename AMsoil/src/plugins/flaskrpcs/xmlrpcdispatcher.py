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
        """Retrieve the certificate which the client has sent. If using the development server, the certificate is read from a static file (see config keys)."""
        # get it from the request's environment
        if request.environ.has_key('CLIENT_RAW_CERT'):
            return request.environ['CLIENT_RAW_CERT']
        
        # unfortunately, werkzeug (the server behind flask) can not handle client certificates
        # hence we fake it by using a file configured by the user
        config = pm.getService("config")
        if config.get("flask.debug") and not config.get("flask.fcgi"):
            try:
                return open(expand_amsoil_path(config.get("flask.debug.client_cert_file")), 'r').read()
            except:
                raise exceptions.DebugClientCertNotFound()
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
