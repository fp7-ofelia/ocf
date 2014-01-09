import os, os.path
import urllib2
import traceback
from datetime import datetime
from dateutil import parser as dateparser

from lxml import etree
from lxml.builder import ElementMaker

import ext.geni
import ext.sfa.trust.gid as gid

import amsoil.core.pluginmanager as pm
from amsoil.core import serviceinterface
from amsoil.config import ROOT_PATH
import amsoil.core.log
logger=amsoil.core.log.getLogger('geniv2rpc')

from amsoil.config import expand_amsoil_path

from exceptions import *

xmlrpc = pm.getService('xmlrpc')

class GENIv2Handler(xmlrpc.Dispatcher):
    RFC3339_FORMAT_STRING = '%Y-%m-%d %H:%M:%S.%fZ'
    
    def __init__(self):
        super(GENIv2Handler, self).__init__(logger)
        self._delegate = None
        logger.info("SETTING GENIv2 DELEGATE: None")
    
    @serviceinterface
    def setDelegate(self, geniv2delegate):
        self._delegate = geniv2delegate
        logger.info("SETTING GENIv2 DELEGATE: %s" % geniv2delegate)
    
    @serviceinterface
    def getDelegate(self):
        return self._delegate


    # RSPEC3_NAMESPACE= 'http://www.geni.net/resources/rspec/3'
    
    def GetVersion(self):
        """Returns the version of this interface.
        This method can be hard coded, since we are actually setting up the GENI v2 API, only.
        For the RSpec extensions, we ask the delegate."""
        # no authentication necessary
        
        try:
            request_extensions = self._delegate.get_request_extensions_list()
            ad_extensions = self._delegate.get_ad_extensions_list()
            allocation_mode = self._delegate.get_allocation_mode()
            is_single_allocation = self._delegate.is_single_allocation()
        except Exception as e:
            return self._errorReturn(e)
                
        request_rspec_versions = [
            { 'type' : 'geni', 'version' : '2', 'schema' : 'http://www.geni.net/resources/rspec/2/request.xsd', 'namespace' : 'http://www.geni.net/resources/rspec/2', 'extensions' : request_extensions},]
        ad_rspec_versions = [
                { 'type' : 'geni', 'version' : '2', 'schema' : 'http://www.geni.net/resources/rspec/2/ad.xsd', 'namespace' : 'http://www.geni.net/resources/rspec/2', 'extensions' : ad_extensions },]
        credential_types = { 'geni_type' : 'geni_sfa', 'geni_version' : '2' }
    
        return self._successReturn({ 
                'geni_api'                    : '2',
                'geni_api_versions'           : { '2' : '/geni2' }, # this should be an absolute URL
                'geni_request_rspec_versions' : request_rspec_versions,
                'geni_ad_rspec_versions'      : ad_rspec_versions,
                'geni_credential_types'       : credential_types,
                'geni_single_allocation'      : is_single_allocation,
                'geni_allocate'               : allocation_mode
                })

    def ListResources(self, credentials, options):
        """Delegates the call and unwraps the needed parameter. Also takes care of the compression option."""
        # interpret options
        geni_available = bool(options['geni_available']) if ('geni_available' in options) else False
        geni_compress = bool(options['geni_compress']) if ('geni_compress' in options) else False

        # check version and delegate
        try:
            self._checkRSpecVersion(options['geni_rspec_version'])
            result = self._delegate.list_resources(self.requestCertificate(), credentials, geni_available)
        except Exception as e:
            return self._errorReturn(e)
        # compress and return
        if geni_compress:
            result = base64.b64encode(zlib.compress(result))
        return self._successReturn(result)

    def CreateSliver(self, slice_urn, credentials, rspec, users, options):
        """
        Allocate (GENI v3).
        Delegates the call and unwraps the needed parameter. Also converts the incoming timestamp to python and the outgoing to geni compliant date format.
        """
        geni_end_time = self._str2datetime(options['geni_end_time']) if ('geni_end_time' in options) else None
        # TODO check the end_time against the duration of the credential
        try:
            # delegate
            # self._checkRSpecVersion(options['geni_rspec_version']) # omni does not send this option
            result_rspec, result_sliver_list = self._delegate.allocate(slice_urn, self.requestCertificate(), credentials, rspec, geni_end_time)
            # change datetime's to strings
            result = { 'geni_rspec' : result_rspec, 'geni_slivers' : self._convertExpiresDate(result_sliver_list) }
        except Exception as e:
            return self._errorReturn(e)
        """
        Provision.
        """
        geni_best_effort = bool(options['geni_best_effort']) if ('geni_best_effort' in options) else True
        geni_end_time = self._str2datetime(options['geni_end_time']) if ('geni_end_time' in options) else None
        geni_users = options['geni_users'] if ('geni_users' in options) else []
        # TODO check the end_time against the duration of the credential
        try:
            self._checkRSpecVersion(options['geni_rspec_version'])
            result_rspec, result_sliver_list = self._delegate.provision(slice_urn, self.requestCertificate(), credentials, geni_best_effort, geni_end_time, geni_users)
            result = { 'geni_rspec' : result_rspec, 'geni_slivers' : self._convertExpiresDate(result_sliver_list) }
        except Exception as e:
            return self._errorReturn(e)
        """
        Perform operational action (GENI v3). Values = {StartSliver, StopSliver, RestartSliver}
        """
        action = "StartSliver" #, StopSliver, and RestartSliver 
        geni_best_effort = bool(options['geni_best_effort']) if ('geni_best_effort' in options) else False
        try:
            result = self._delegate.perform_operational_action(slice_urn, self.requestCertificate(), credentials, action, geni_best_effort)
            result = self._convertExpiresDate(result)
        except Exception as e:
            return self._errorReturn(e)
        return self._successReturn(result)

    def RenewSliver(self, slice_urn, credentials, expiration_time_str, options):
        geni_best_effort = bool(options['geni_best_effort']) if ('geni_best_effort' in options) else True
        expiration_time = self._str2datetime(expiration_time_str)
        try:
            # delegate
            result = self._delegate.renew(slice_urn, self.requestCertificate(), credentials, expiration_time, geni_best_effort)
            # change datetime's to strings
            result = self._convertExpiresDate(result)
        except Exception as e:
            return self._errorReturn(e)
        return self._successReturn(result)
    
    def SliverStatus(self, slice_urn, credentials, options):
        try:
            result_sliceurn, result_sliver_list = self._delegate.status(slice_urn, credentials, options)
            result = { 'geni_urn' : result_sliceurn, 'geni_slivers' : self._convertExpiresDate(result_sliver_list) }
        except Exception as e:
            return self._errorReturn(e)
        return self._successReturn(result)

    def DeleteSliver(self, slice_urn, credentials, options):
        geni_best_effort = bool(options['geni_best_effort']) if ('geni_best_effort' in options) else False
        try:
            result = self._delegate.delete(slice_urn, self.requestCertificate(), credentials, geni_best_effort)
            result = self._convertExpiresDate(result)
        except Exception as e:
            return self._errorReturn(e)
        return self._successReturn(result)

    def Shutdown(self, slice_urn, credentials, options):
        try:
            result = bool(self._delegate.shutdown(slice_urn, self.requestCertificate(), credentials))
        except Exception as e:
            return self._errorReturn(e)
        return self._successReturn(result)


    # ---- helper methods
    def _datetime2str(self, dt):
        return dt.strftime(self.RFC3339_FORMAT_STRING)

    def _str2datetime(self, strval):
        """Parses the given date string and converts the timestamp to utc and the date unaware of timezones."""
        result = dateparser.parse(strval)
        if result:
            result = result - result.utcoffset()
            result = result.replace(tzinfo=None)
        return result

    def _convertExpiresDate(self, sliver_list):
        for slhash in sliver_list:
            if slhash['geni_expires'] == None:
                continue
            if not isinstance(slhash['geni_expires'], datetime):
                raise ValueError("Given geni_expires in sliver_list hash retrieved from delegate's method is not a python datetime object.")
            slhash['geni_expires'] = self._datetime2str(slhash['geni_expires'])
        return sliver_list

    def _checkRSpecVersion(self, rspec_version_option):
        if (int(rspec_version_option['version']) != 2) or (rspec_version_option['type'].lower() != 'geni'):
            raise GENIv2BadArgsError("Only RSpec 2 supported.")
        
    def _errorReturn(self, e):
        """Assembles a GENI compliant return result for faulty methods."""
        if not isinstance(e, GENIv2BaseError): # convert common errors into GENIv2GeneralError
            e = GENIv2ServerError(str(e))
        # do some logging
        logger.error(e)
        logger.error(traceback.format_exc())
        return { 'geni_api' : 2, 'code' : { 'geni_code' : e.code }, 'output' : str(e) }
        
    def _successReturn(self, result):
        """Assembles a GENI compliant return result for successful methods."""
        return { 'geni_api' : 2, 'code' : { 'geni_code' : 0 }, 'value' : result, 'output' : None }



class GENIv2DelegateBase(object):
    """
    TODO document
    The GENIv2 handler assumes that this class uses RSpec version 2 when interacting with the client.
    
    General parameters:
    {client_cert} The client's certificate. See [flaskrpcs]XMLRPCDispatcher.requestCertificate(). Also see http://groups.geni.net/geni/wiki/GeniApiCertificates
    {credentials} The a list of credentials in the format specified at http://groups.geni.net/geni/wiki/GAPI_AM_API_V2/CommonConcepts#credentials

    Dates are converted to UTC and then made timezone-unaware (see http://docs.python.org/2/library/datetime.html#datetime.datetime.astimezone).
    """
    
    ALLOCATION_STATE_UNALLOCATED = 'geni_unallocated'
    """The sliver does not exist. (see http://groups.geni.net/geni/wiki/GAPI_AM_API_V2/CommonConcepts#SliverAllocationStates)"""
    ALLOCATION_STATE_ALLOCATED = 'geni_allocated'
    """The sliver is offered/promissed, but it does not consume actual resources. This state shall time out at some point in time."""
    ALLOCATION_STATE_PROVISIONED = 'geni_provisioned'
    """The sliver is/has been instanciated. Operational states apply here."""

    OPERATIONAL_STATE_PENDING_ALLOCATION = 'geni_pending_allocation'
    """Required for aggregates to support. A transient state."""
    OPERATIONAL_STATE_NOTREADY           = 'geni_notready'
    """Optional. A stable state."""
    OPERATIONAL_STATE_CONFIGURING        = 'geni_configuring'
    """Optional. A transient state."""
    OPERATIONAL_STATE_STOPPING           = 'geni_stopping'
    """Optional. A transient state."""
    OPERATIONAL_STATE_READY              = 'geni_ready'
    """Optional. A stable state."""
    OPERATIONAL_STATE_READY_BUSY         = 'geni_ready_busy'
    """Optional. A transient state."""
    OPERATIONAL_STATE_FAILED             = 'geni_failed'
    """Optional. A stable state."""

    OPERATIONAL_ACTION_START   = 'geni_start'
    """Sliver shall become geni_ready. The AM developer may define more states (see http://groups.geni.net/geni/wiki/GAPI_AM_API_V2/CommonConcepts#SliverOperationalActions)"""
    OPERATIONAL_ACTION_RESTART = 'geni_restart'
    """Sliver shall become geni_ready again."""
    OPERATIONAL_ACTION_STOP    = 'geni_stop'
    """Sliver shall become geni_notready."""

    def __init__(self):
        super(GENIv2DelegateBase, self).__init__()
        pass
    
    def get_request_extensions_list(self):
        """Not to overwrite by AM developer. Should retrun a list of request extensions (XSD schemas) to be sent back by GetVersion."""
        return [uri for prefix, uri in self.get_request_extensions_mapping().items()]

    def get_request_extensions_mapping(self):
        """Overwrite by AM developer. Should return a dict of namespace names and request extensions (XSD schema's URLs as string).
        Format: {xml_namespace_prefix : namespace_uri, ...}
        """
        return {}

    def get_manifest_extensions_mapping(self):
        """Overwrite by AM developer. Should return a dict of namespace names and manifest extensions (XSD schema's URLs as string).
        Format: {xml_namespace_prefix : namespace_uri, ...}
        """
        return {}
        
    def get_ad_extensions_list(self):
        """Not to overwrite by AM developer. Should retrun a list of request extensions (XSD schemas) to be sent back by GetVersion."""
        return [uri for prefix, uri in self.get_ad_extensions_mapping().items()]

    def get_ad_extensions_mapping(self):
        """Overwrite by AM developer. Should return a dict of namespace names and advertisement extensions (XSD schema URLs as string) to be sent back by GetVersion.
        Format: {xml_namespace_prefix : namespace_uri, ...}
        """
        return {}
    
    def is_single_allocation(self):
        """Overwrite by AM developer. Shall return a True or False. When True (not default), and performing one of (Describe, Allocate, Renew, Provision, Delete), such an AM requires you to include either the slice urn or the urn of all the slivers in the same state.
        see http://groups.geni.net/geni/wiki/GAPI_AM_API_V2/CommonConcepts#OperationsonIndividualSlivers"""
        return False

    def get_allocation_mode(self):
        """Overwrite by AM developer. Shall return a either 'geni_single', 'geni_disjoint', 'geni_many'.
        It defines whether this AM allows adding slivers to slices at an AM (i.e. calling Allocate multiple times, without first deleting the allocated slivers).
        For description of the options see http://groups.geni.net/geni/wiki/GAPI_AM_API_V2/CommonConcepts#OperationsonIndividualSlivers"""
        return 'geni_single'

    def list_resources(self, client_cert, credentials, geni_available):
        """Overwrite by AM developer. Shall return an RSpec version 2 (advertisement) or raise an GENIv2...Error.
        If {geni_available} is set, only return availabe resources.
        For full description see http://groups.geni.net/geni/wiki/GAPI_AM_API_V2#ListResources"""
        raise GENIv2GeneralError("Method not implemented yet")

    def allocate(self, slice_urn, client_cert, credentials, rspec, end_time=None):
        """Overwrite by AM developer. 
        Shall return the two following values or raise an GENIv2...Error.
        - a RSpec version 2 (manifest) of newly allocated slivers 
        - a list of slivers of the format:
            [{'geni_sliver_urn' : String,
              'geni_expires'    : Python-Date,
              'geni_allocation_status' : one of the ALLOCATION_STATE_xxx}, 
             ...]
        Please return like so: "return respecs, slivers"
        {slice_urn} contains a slice identifier (e.g. 'urn:publicid:IDN+ofelia:eict:gcf+slice+myslice').
        {end_time} Optional. A python datetime object which determines the desired expiry date of this allocation (see http://groups.geni.net/geni/wiki/GAPI_AM_API_V2/CommonConcepts#geni_end_time).
        >>> This is the first part of what CreateSliver used to do in previous versions of the AM API. The second part is now done by Provision, and the final part is done by PerformOperationalAction.
        
        For full description see http://groups.geni.net/geni/wiki/GAPI_AM_API_V2#Allocate"""
        raise GENIv2GeneralError("Method not implemented yet")

    def renew(self, slice_urn, client_cert, credentials, expiration_time, best_effort):
        """Overwrite by AM developer. 
        Shall return a sliver of the following format or raise an GENIv2...Error:
            {'geni_sliver_urn'         : String,
              'geni_allocation_status'  : one of the ALLOCATION_STATE_xxx,
              'geni_operational_status' : one of the OPERATIONAL_STATE_xxx,
              'geni_expires'            : Python-Date,
              'geni_error'              : optional String}, 
             ...
        
        {urns} contains a slice identifier (e.g. 'urn:publicid:IDN+ofelia:eict:gcf+slice+myslice').
        {expiration_time} is a python datetime object
        {best_effort} determines if the method shall fail in case that not all of the urns can be renewed (best_effort=False).

        If the transactional behaviour of {best_effort}=False can not be provided, throw a GENIv2OperationUnsupportedError.
        For more information on possible {urns} see http://groups.geni.net/geni/wiki/GAPI_AM_API_V2/CommonConcepts#urns

        For full description see http://groups.geni.net/geni/wiki/GAPI_AM_API_V2#Renew"""
        raise GENIv2GeneralError("Method not implemented yet")

    def provision(self, slice_urn, client_cert, credentials, best_effort, end_time, geni_users):
        """Overwrite by AM developer. 
        Shall return the two following values or raise an GENIv2...Error.
        - a RSpec version 2 (manifest) of slivers 
        - a sliver of the format:
            {'geni_sliver_urn'         : String,
              'geni_allocation_status'  : one of the ALLOCATION_STATE_xxx,
              'geni_operational_status' : one of the OPERATIONAL_STATE_xxx,
              'geni_expires'            : Python-Date,
              'geni_error'              : optional String}, 
             ...
        Please return like so: "return respec, sliver"

        {urns} contains a slice/resource identifier (e.g. ['urn:publicid:IDN+ofelia:eict:gcf+slice+myslice']).
        {best_effort} determines if the method shall fail in case that not all of the urns can be provisioned (best_effort=False)
        {end_time} Optional. A python datetime object which determines the desired expiry date of this provision (see http://groups.geni.net/geni/wiki/GAPI_AM_API_V2/CommonConcepts#geni_end_time).
        {geni_users} is a list of the format: [ { 'urn' : ..., 'keys' : [sshkey, ...]}, ...]
        
        If the transactional behaviour of {best_effort}=False can not be provided, throw a GENIv2OperationUnsupportedError.
        For more information on possible {urns} see http://groups.geni.net/geni/wiki/GAPI_AM_API_V2/CommonConcepts#urns

        For full description see http://groups.geni.net/geni/wiki/GAPI_AM_API_V2#Provision"""
        raise GENIv2GeneralError("Method not implemented yet")

    def status(self, slice_urn, credentials, options):
        """Overwrite by AM developer. 
        Shall return the two following values or raise an GENIv2...Error.
        - a slice urn
        - a sliver of the format:
            {'geni_sliver_urn'         : String,
              'geni_allocation_status'  : one of the ALLOCATION_STATE_xxx,
              'geni_operational_status' : one of the OPERATIONAL_STATE_xxx,
              'geni_expires'            : Python-Date,
              'geni_error'              : optional String}, 
             ...
        Please return like so: "return slice_urn, sliver"

        {urns} contains a list of slice/resource identifiers (e.g. ['urn:publicid:IDN+ofelia:eict:gcf+slice+myslice']).
        For more information on possible {urns} see http://groups.geni.net/geni/wiki/GAPI_AM_API_V2/CommonConcepts#urns
        
        For full description see http://groups.geni.net/geni/wiki/GAPI_AM_API_V2#Status"""
        raise GENIv2GeneralError("Method not implemented yet")

    def perform_operational_action(self, slice_urn, client_cert, credentials, action, best_effort):
        """Overwrite by AM developer. 
        Shall return a sliver of the following format or raise an GENIv2...Error:
            {'geni_sliver_urn'         : String,
              'geni_allocation_status'  : one of the ALLOCATION_STATE_xxx,
              'geni_operational_status' : one of the OPERATIONAL_STATE_xxx,
              'geni_expires'            : Python-Date,
              'geni_error'              : optional String}, 
             ...

        {urns} contains a list of slice or sliver identifiers (e.g. ['urn:publicid:IDN+ofelia:eict:gcf+slice+myslice']).
        {action} an arbitraty string, but the following should be possible: "geni_start", "geni_stop", "geni_restart"
        {best_effort} determines if the method shall fail in case that not all of the urns can be changed (best_effort=False)

        If the transactional behaviour of {best_effort}=False can not be provided, throw a GENIv2OperationUnsupportedError.
        For more information on possible {urns} see http://groups.geni.net/geni/wiki/GAPI_AM_API_V2/CommonConcepts#urns
        
        For full description see http://groups.geni.net/geni/wiki/GAPI_AM_API_V2#PerformOperationalAction"""
        raise GENIv2GeneralError("Method not implemented yet")

    def delete(self, slice_urn, client_cert, credentials, best_effort):
        """Overwrite by AM developer. 
        Shall return a sliver of the following format or raise an GENIv2...Error:
            {'geni_sliver_urn'         : String,
              'geni_allocation_status'  : one of the ALLOCATION_STATE_xxx,
              'geni_expires'            : Python-Date,
              'geni_error'              : optional String}, 
             ...

        {urns} contains a list of slice/resource identifiers (e.g. ['urn:publicid:IDN+ofelia:eict:gcf+slice+myslice']).
        {best_effort} determines if the method shall fail in case that not all of the urns can be deleted (best_effort=False)
        
        If the transactional behaviour of {best_effort}=False can not be provided, throw a GENIv2OperationUnsupportedError.
        For more information on possible {urns} see http://groups.geni.net/geni/wiki/GAPI_AM_API_V2/CommonConcepts#urns

        For full description see http://groups.geni.net/geni/wiki/GAPI_AM_API_V2#Delete"""
        raise GENIv2GeneralError("Method not implemented yet")

    def shutdown(self, slice_urn, client_cert, credentials):
        """Overwrite by AM developer. 
        Shall return True or False or raise an GENIv2...Error.

        For full description see http://groups.geni.net/geni/wiki/GAPI_AM_API_V2#Shutdown"""
        raise GENIv2GeneralError("Method not implemented yet")
    
    @serviceinterface
    def auth(self, client_cert, credentials, slice_urn=None, privileges=()):
        """
        This method authenticates and authorizes.
        It returns the client's urn, uuid, email (extracted from the {client_cert}). Example call: "urn, uuid, email = self.auth(...)"
        Be aware, the email is not required in the certificate, hence it might be empty.
        If the validation fails, an GENIv2ForbiddenError is thrown.
        
        The credentials are checked so the user has all the required privileges (success if any credential fits all privileges).
        The client certificate is not checked: this is usually done via the webserver configuration.
        This method only treats certificates of type 'geni_sfa'.
        
        Here a list of possible privileges (format: right_in_credential: [privilege1, privilege2, ...]):
            "authority" : ["register", "remove", "update", "resolve", "list", "getcredential", "*"],
            "refresh"   : ["remove", "update"],
            "resolve"   : ["resolve", "list", "getcredential"],
            "sa"        : ["getticket", "redeemslice", "redeemticket", "createslice", "createsliver", "deleteslice", "deletesliver", "updateslice",
                           "getsliceresources", "getticket", "loanresources", "stopslice", "startslice", "renewsliver",
                            "deleteslice", "deletesliver", "resetslice", "listslices", "listnodes", "getpolicy", "sliverstatus"],
            "embed"     : ["getticket", "redeemslice", "redeemticket", "createslice", "createsliver", "renewsliver", "deleteslice", 
                           "deletesliver", "updateslice", "sliverstatus", "etsliceresources", "shutdown"],
            "bind"      : ["getticket", "loanresources", "redeemticket"],
            "control"   : ["updateslice", "createslice", "createsliver", "renewsliver", "sliverstatus", "stopslice", "startslice", 
                           "deleteslice", "deletesliver", "resetslice", "getsliceresources", "getgids"],
            "info"      : ["listslices", "listnodes", "getpolicy"],
            "ma"        : ["setbootstate", "getbootstate", "reboot", "getgids", "gettrustedcerts"],
            "operator"  : ["gettrustedcerts", "getgids"],                   
            "*"         : ["createsliver", "deletesliver", "sliverstatus", "renewsliver", "shutdown"]
            
        When using the gcf clearinghouse implementation the credentials will have the rights:
        - user: "refresh", "resolve", "info" (which resolves to the privileges: "remove", "update", "resolve", "list", "getcredential", "listslices", "listnodes", "getpolicy").
        - slice: "refresh", "embed", "bind", "control", "info" (well, do the resolving yourself...)        
        """
        # check variables
        if not isinstance(privileges, tuple):
            raise TypeError("Privileges need to be a tuple.")
        # collect credentials (only GENI certs, version ignored)
        geni_credentials = []
        for c in credentials:
             if c['geni_type'] == 'geni_sfa':
                 geni_credentials.append(c['geni_value'])

        # get the cert_root
        config = pm.getService("config")
        cert_root = expand_amsoil_path(config.get("geniv2rpc.cert_root"))

        if client_cert == None:
            raise GENIv2ForbiddenError("Could not determine the client SSL certificate")
        # test the credential
        try:
            cred_verifier = ext.geni.CredentialVerifier(cert_root)
            cred_verifier.verify_from_strings(client_cert, geni_credentials, slice_urn, privileges)
        except Exception as e:
            raise GENIv2ForbiddenError(str(e))
        
        user_gid = gid.GID(string=client_cert)
        user_urn = user_gid.get_urn()
        user_uuid = user_gid.get_uuid()
        user_email = user_gid.get_email()
        return user_urn, user_uuid, user_email # TODO document return

    @serviceinterface
    def urn_type(self, urn):
        """Returns the type of the urn (e.g. slice, sliver).
        For the possible types see: http://groups.geni.net/geni/wiki/GeniApiIdentifiers#ExamplesandUsage"""
        return urn.split('+')[2].strip()

    @serviceinterface
    def lxml_ad_root(self):
        """Returns a xml root node with the namespace extensions specified by self.get_ad_extensions_mapping."""
        return etree.Element('rspec', self.get_ad_extensions_mapping(), type='advertisement')

    def lxml_manifest_root(self):
        """Returns a xml root node with the namespace extensions specified by self.get_manifest_extensions_mapping."""
        return etree.Element('rspec', self.get_manifest_extensions_mapping(), type='manifest')

    @serviceinterface
    def lxml_to_string(self, rspec):
        """Converts a lxml root node to string (for returning to the client)."""
        return etree.tostring(rspec, pretty_print=True)
        
    @serviceinterface
    def lxml_ad_element_maker(self, prefix):
        """Returns a lxml.builder.ElementMaker configured for avertisements and the namespace given by {prefix}."""
        ext = self.get_ad_extensions_mapping()
        return ElementMaker(namespace=ext[prefix], nsmap=ext)

    @serviceinterface
    def lxml_manifest_element_maker(self, prefix):
        """Returns a lxml.builder.ElementMaker configured for manifests and the namespace given by {prefix}."""
        ext = self.get_manifest_extensions_mapping()
        return ElementMaker(namespace=ext[prefix], nsmap=ext)

    @serviceinterface
    def lxml_parse_rspec(self, rspec_string):
        """Returns a the root element of the given {rspec_string} as lxml.Element.
        If the config key is set, the rspec is validated with the schemas found at the URLs specified in schemaLocation of the the given RSpec."""
        # parse
        rspec_root = etree.fromstring(rspec_string)
        # validate RSpec against specified schemaLocations
        config = pm.getService("config")
        should_validate = config.get("geniv2rpc.rspec_validation")

        if should_validate:
            schema_locations = rspec_root.get("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation")
            if schema_locations:
                schema_location_list = schema_locations.split(" ")
                schema_location_list = map(lambda x: x.strip(), schema_location_list) # strip whitespaces
                for sl in schema_location_list:
                    try:
                        xmlschema_contents = urllib2.urlopen(sl) # try to download the schema
                        xmlschema_doc = etree.parse(xmlschema_contents)
                        xmlschema = etree.XMLSchema(xmlschema_doc)
                        xmlschema.validate(rspec_root)
                    except Exception as e:
                        logger.warning("RSpec validation failed failed (%s: %s)" % (sl, str(e),))
            else:
                logger.warning("RSpec does not specify any schema locations")
        return rspec_root

    @serviceinterface
    def lxml_elm_has_request_prefix(self, lxml_elm, ns_name):
        return str(lxml_elm.tag).startswith("{%s}" % (self.get_request_extensions_mapping()[ns_name],))
    # def lxml_request_prefix(self, ns_name):
    #     """Returns the full lxml-prefix: Wraps the namespace looked up in the get_request_extensions_mapping (see above) wrapped in curly brackets (useful for lxml)."""
    #     return "{%s}" % (self.get_request_extensions_mapping()[ns_name],)
    # @serviceinterface
    # def lxml_mainifest_prefix(self, ns_name):
    #     """See: lxml_request_prefix() (here for manifest)"""
    #     return "{%s}" % (self.get_manifest_extensions_mapping()[ns_name],)
    # @serviceinterface
    # def lxml_ad_prefix(self, ns_name):
    #     """See: lxml_request_prefix() (here for advertisement)"""
    #     return "{%s}" % (self.get_ad_extensions_mapping()[ns_name],)
        
    @serviceinterface
    def lxml_elm_equals_request_tag(self, lxml_elm, ns_name, tagname):
        """Determines if the given tag by {ns_name} and {tagname} equals lxml_tag. The namespace URI is looked up via get_request_extensions_mapping()['ns_name']"""
        return ("{%s}%s" % (self.get_request_extensions_mapping()[ns_name], tagname)) == str(lxml_elm.tag)
        
