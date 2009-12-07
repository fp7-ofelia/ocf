#
# PLCAPI XML-RPC and SOAP interfaces
#
# Aaron Klingaman <alk@absarokasoft.com>
# Mark Huang <mlhuang@cs.princeton.edu>
#
# Copyright (C) 2004-2006 The Trustees of Princeton University
# $Id: API.py 14587 2009-07-19 13:18:50Z thierry $
# $URL: https://svn.planet-lab.org/svn/PLCAPI/trunk/PLC/API.py $
#

import sys
import traceback
import string

import xmlrpclib
import logging
import logging.handlers

from ApiExceptionCodes import *

# Wrapper around xmlrpc fault to include a traceback of the server to the
# client. This is done to aid in debugging from a client perspective.

class FaultWithTraceback(xmlrpclib.Fault):
    def __init__(self, code, faultString, exc_info):
        type, value, tb = exc_info
        exc_str = ''.join(traceback.format_exception(type, value, tb))
        faultString = faultString + "\nFAULT_TRACEBACK:" + exc_str
        xmlrpclib.Fault.__init__(self, code, faultString)

# Exception to report to the caller when some non-XMLRPC fault occurs on the
# server. For example a TypeError.

class UnhandledServerException(FaultWithTraceback):
    def __init__(self, exc_info):
        type, value, tb = exc_info
        faultString = "Unhandled exception: " + str(type)
        FaultWithTraceback.__init__(self, FAULT_UNHANDLEDSERVEREXCEPTION, faultString, exc_info)

# See "2.2 Characters" in the XML specification:
#
# #x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD]
# avoiding
# [#x7F-#x84], [#x86-#x9F], [#xFDD0-#xFDDF]

invalid_xml_ascii = map(chr, range(0x0, 0x8) + [0xB, 0xC] + range(0xE, 0x1F))
xml_escape_table = string.maketrans("".join(invalid_xml_ascii), "?" * len(invalid_xml_ascii))

def xmlrpclib_escape(s, replace = string.replace):
    """
    xmlrpclib does not handle invalid 7-bit control characters. This
    function augments xmlrpclib.escape, which by default only replaces
    '&', '<', and '>' with entities.
    """

    # This is the standard xmlrpclib.escape function
    s = replace(s, "&", "&amp;")
    s = replace(s, "<", "&lt;")
    s = replace(s, ">", "&gt;",)

    # Replace invalid 7-bit control characters with '?'
    return s.translate(xml_escape_table)

def xmlrpclib_dump(self, value, write):
    """
    xmlrpclib cannot marshal instances of subclasses of built-in
    types. This function overrides xmlrpclib.Marshaller.__dump so that
    any value that is an instance of one of its acceptable types is
    marshalled as that type.

    xmlrpclib also cannot handle invalid 7-bit control characters. See
    above.
    """

    # Use our escape function
    args = [self, value, write]
    if isinstance(value, (str, unicode)):
        args.append(xmlrpclib_escape)

    try:
        # Try for an exact match first
        f = self.dispatch[type(value)]
    except KeyError:
        # Try for an isinstance() match
        for Type, f in self.dispatch.iteritems():
            if isinstance(value, Type):
                f(*args)
                return
        raise TypeError, "cannot marshal %s objects" % type(value)
    else:
        f(*args)

# You can't hide from me!
xmlrpclib.Marshaller._Marshaller__dump = xmlrpclib_dump

# SOAP support is optional
try:
    import SOAPpy
    from SOAPpy.Parser import parseSOAPRPC
    from SOAPpy.Types import faultType
    from SOAPpy.NS import NS
    from SOAPpy.SOAPBuilder import buildSOAP
except ImportError:
    SOAPpy = None

def import_deep(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

class BaseApi:
    def __init__(self, encoding = "utf-8"):
        self.encoding = encoding
        self.init_logger()
        self.funcs = {}
        self.register_functions()

    def init_logger(self):
        self.logger = logging.getLogger("ApiLogger")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.handlers.RotatingFileHandler(self.get_log_name(), maxBytes=100000, backupCount=5))

    def get_log_name(self):
        return "/tmp/apilogfile.txt"

    def register_functions(self):
        self.register_function(self.noop)

    def register_function(self, function, name = None):
        if name is None:
            name = function.__name__
        self.funcs[name] = function

    def call(self, source, method, *args):
        """
        Call the named method from the specified source with the
        specified arguments.
        """

        if not method in self.funcs:
            raise "Unknown method: " + method

        return self.funcs[method](*args)

    def handle(self, source, data):
        """
        Handle an XML-RPC or SOAP request from the specified source.
        """

        # Parse request into method name and arguments
        try:
            interface = xmlrpclib
            (args, method) = xmlrpclib.loads(data)
            methodresponse = True
        except Exception, e:
            if SOAPpy is not None:
                interface = SOAPpy
                (r, header, body, attrs) = parseSOAPRPC(data, header = 1, body = 1, attrs = 1)
                method = r._name
                args = r._aslist()
                # XXX Support named arguments
            else:
                raise e

        self.logger.debug("OP:" + str(method) + " from " + str(source))

        try:
            result = self.call(source, method, *args)
        except xmlrpclib.Fault, fault:
            self.logger.warning("FAULT: " + str(fault.faultCode) + " " + str(fault.faultString))
            self.logger.info(traceback.format_exc())
            # Handle expected faults
            if interface == xmlrpclib:
                result = FaultWithTraceback(fault.faultCode, fault.faultString, sys.exc_info())
                methodresponse = None
            elif interface == SOAPpy:
                result = faultParameter(NS.ENV_T + ":Server", "Method Failed", method)
                result._setDetail("Fault %d: %s" % (fault.faultCode, fault.faultString))
                self.logger.debug
        except:
            self.logger.warning("EXCEPTION: " + str(sys.exc_info()[0]))
            self.logger.info(traceback.format_exc())
            result = UnhandledServerException(sys.exc_info())
            methodresponse = None

        # Return result
        if interface == xmlrpclib:
            if not isinstance(result, xmlrpclib.Fault):
                result = (result,)
            data = xmlrpclib.dumps(result, methodresponse = True, encoding = self.encoding, allow_none = 1)
        elif interface == SOAPpy:
            data = buildSOAP(kw = {'%sResponse' % method: {'Result': result}}, encoding = self.encoding)

        return data

    def noop(self, value):
        return value



