from flup.server.fcgi import WSGIServer
from flaskext.xmlrpc import XMLRPCHandler, Fault

from xmlrpcdispatcher import XMLRPCDispatcher

from amsoil.core import serviceinterface

class FlaskXMLRPC(object):
    """
    Encapsulates an XML-RPC receiver within a flask server.
    It also exports the service xmlrpc, which has the service contract outlined below.
    Along with the class reference provided by Dispatcher the contract also implies:
    - All receiver instances which can be registered via registerXMLRPC need to derrive from the Dispatcher class given below.
    - The Dispatcher is responsible for protecting private methods (starts with '_').
    - The Dispatcher is responsible for catching errors (as last resort) and converting them to reasonable messages which are passed back to the user.
    - The Dispatcher is responsible for logging if so desired by the admin.
    - The Dispatcher offers a method called {requestCertificate}, which returns the current request's SSL certificate or None, if there wasn't any.
    - The registered instance's method gets called when the XMLRPC call comes in (e.g. client sends bla(x), instance.bla(self, x) gets called).
    - These method's return value gets passed back to the user.
    """
    def __init__(self, flaskapp):
        self._flaskapp = flaskapp

    @property
    @serviceinterface
    def Dispatcher(self):
        """Base class for all XMLRPC receivers which register for registerXMLRPC(...)"""
        return XMLRPCDispatcher

    @serviceinterface
    def registerXMLRPC(self, unique_service_name, instance, endpoint):
        """Register the receiver.
        {unique_service_name} just has to be a unique name (dont ask why).
        The {instance} is an object (an {Dispatcher} instance) providing the methods which get called via the XMLRPC enpoint.
        {endpoint} is the mounting point for the XML RPC interface (e.g. '/geni' )."""
        # TODO only set the ClientCert Handler if configured
        handler = XMLRPCHandler(unique_service_name)
        handler.connect(self._flaskapp.app, endpoint)
        handler.register_instance(instance)

