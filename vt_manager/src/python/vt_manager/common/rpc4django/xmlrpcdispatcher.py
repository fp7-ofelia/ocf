"""
Implements an XMLRPC dispatcher
"""

import sys
import xmlrpclib
from xmlrpclib import Fault
from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
import traceback


class XMLRPCDispatcher(SimpleXMLRPCDispatcher):
    """
    Encodes and decodes XMLRPC messages, dispatches to the requested method
    and returns any responses or errors in encoded XML.

    This class is modified from the built-in python version so that it can
    also pass the HttpRequest object from the underlying request
    """

    def __init__(self):
        self.funcs = {}
        self.instance = None
        self.allow_none = True
        self.encoding = None

    def dispatch(self, data, **kwargs):
        """
        Extracts the xml marshaled parameters and method name and calls the
        underlying method and returns either an xml marshaled response
        or an XMLRPC fault

        Although very similar to the superclass' _marshaled_dispatch, this
        method has a different name due to the different parameters it takes
        from the superclass method.
        """

        try:
            params, method = xmlrpclib.loads(data)
            # Speaks-for
            try:
                caller_cert = kwargs['request'].META['SSL_CLIENT_CERT']
                if caller_cert:
                    params = params + (kwargs['request'].META['SSL_CLIENT_CERT'],)
            except Exception as e:
                print("Speaks-for: error on retrieving SSL_CLIENT_CERT. \
                    Details: " + e)
            try:
                response = self._dispatch(method, params, **kwargs)
            except TypeError:
                # Catch unexpected keyword argument error
                response = self._dispatch(method, params)

            # wrap response in a singleton tuple
            response = (response,)
            response = xmlrpclib.dumps(response, methodresponse=1,
                                       allow_none=self.allow_none,
                                       encoding=self.encoding)
        except Fault, fault:
            traceback.print_exc()
            response = xmlrpclib.dumps(fault, allow_none=self.allow_none,
                                       encoding=self.encoding)
        except:
            # report exception back to server
            traceback.print_exc()
            exc_type, exc_value, exc_tb = sys.exc_info()
            response = xmlrpclib.dumps(
                xmlrpclib.Fault(1, "%s:%s" % (exc_type, exc_value)),
                encoding=self.encoding, allow_none=self.allow_none,
                )

        return response

    def _dispatch(self, method, params, **kwargs):
        """
        Dispatches the method with the parameters to the underlying method
        """

        func = self.funcs.get(method, None)

        if func is not None:
            if len(kwargs) > 0:
                return func(*params, **kwargs)
            else:
                return func(*params)
        else:
            raise Exception('method "%s" is not supported' % method)
