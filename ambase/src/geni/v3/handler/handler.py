import base64
import zlib
import datetime

# XXX Isn't this supposed to be used this way?
from src.abstract.classes.handlerbase import HandlerBase
from src.ambase.exceptions import SliceAlreadyExists
from src.ambase.exceptions import AllocationError
from src.ambase.exceptions import ProvisionError
from src.ambase.exceptions import DeleteError
from src.ambase.exceptions import ShutDown
#from src.ambase.exceptions import UnsupportedState
from src.ambase.exceptions import PerformOperationalStateError

class GeniV3Handler(HandlerBase):
       
    def __init__(self):
        self.__delegate= None
        self.__credential_manager = None
        self.__rspec_manager = None
        self.__geni_exception_manager = None
        self.__am_type = None

    def GetVersion(self, options=dict()):
        try:
            value = self.__delegate.get_version()
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.ERROR, e) 
        return self.success_result(value)

    def ListResources(self, credentials=list(), options=dict()):
        # Credential validation
        try:
            self.__credential_manager.validate_for("list_resources", credentials)
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.FORBIDDEN, e)
        
        # Options validation
        if not options.has_key("geni_rspec_version"):
            return self.error_result(self.__geni_exception_manager.BADARGS, 'Bad Arguments: option geni_rspec_version required in options')

        required_options = set(['type', 'version'])
        option_list = set(options['geni_rspec_version'].keys())
        if not required_options.issubset(option_list):
            return self.error_result(self.__geni_exception_manager.BADARGS, 'Bad Arguments: option geni_rspec_version does not have a version, type or geni_rspec_version fields.')
        
        # Retrieving raw resources
        geni_available = False
        if options.get('geni_available'):
            if geni_available:
                geni_available = True
        resources = self.__delegate.list_resources(geni_available)
        
        # Crafting resources into RSpec
        output = self.__rspec_manager.advertise_resources(resources)
        
        
        # Preparing the output
        if 'geni_compressed' in options and options['geni_compressed']:
            output = base64.b64encode(zlib.compress(output))
            
        return self.success_result(output)
        
    def Describe(self, urns=dict(),credentials=dict(),options=dict()):
        # Credential validation
        try:
            self.__credential_manager.validate_for("describe", credentials)
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.FORBIDDEN, e)
        if not options.get('geni_rspec_version'):
            return self.error_result(self.__geni_exception_manager.BADARGS, 'Bad Arguments: option geni_rspec_version does not have a version, type or geni_rspec_version fields.')
        # Options validation
        required_options = set(['type', 'version'])
        option_list = set(options['geni_rspec_version'].keys())
        if not required_options.issubset(option_list):
            return self.error_result(self.__geni_exception_manager.BADARGS, 'Bad Arguments: option geni_rspec_version does not have a version, type or geni_rspec_version fields.')

        # Retrieving slivers to manifest
        slivers = self.__delegate.describe(urns)
        
        # Crafting slivers to manifest RSpec
        output = self.__rspec_manager.manifest_slivers(slivers)
        
        if 'geni_compressed' in options and options['geni_compressed']:
            output = base64.b64encode(zlib.compress(output))
            
        return self.success_result(output)

    def Allocate(self, slice_urn="", credentials=list(), rspec="", options=dict()):
        # Credential validation
        try:
            self.__credential_manager.validate_for("allocate", credentials)
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.FORBIDDEN, e)
        
        am = self.__rspec_manager.parse_request(rspec)
        expiration = self.get_expiration()
        try:
            allocated_slivers = self.__delegate.reserve(slice_urn, am, expiration)    
        except SliceAlreadyExists as e:
            return self.error_result(self.__geni_exception_manager.ALREADYEXISTS, e)
        except AllocationError as e:
            return self.error_result(self.__geni_exception_manager.ERROR, e)

        manifest = self.__rspec_manager.manifest_slivers(allocated_slivers)
        
        return self.success_result(manifest)
        
    def Provision(self, urns=list(), credentials=list(), options=dict()):
        try:
            self.__credential_manager.validate_for("provision", credentials)
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.FORBIDDEN, e)
         
        expiration = self.get_expiration()
        
        if not options.get('geni_rspec_version'):
            return self.error_result(self.__geni_exception_manager.BADARGS, 'Bad Arguments: option geni_rspec_version does not have a version, type or geni_rspec_version fields.')
        # Options validation
        required_options = set(['type', 'version'])
        option_list = set(options['geni_rspec_version'].keys())
        if not required_options.issubset(option_list):
            return self.error_result(self.__geni_exception_manager.BADARGS, 'Bad Arguments: option geni_rspec_version does not have a version, type or geni_rspec_version fields.')

        try:
            slivers = self.__delegate.create(urns)
        except ProvisionError as e:
            return self.error_result(self.__geni_exception_manager.ERROR, e)
        
        manifest = self.__rspec_manager.manifest_slivers(slivers)
        
        return self.success_result(manifest)
    
    def Delete(self, urns=list(), credentials=list(), options=dict()):
        # Credential validation
        try:
            self.__credential_manager.validate_for("delete", credentials)
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.FORBIDDEN, e)
        
        # Calling Delete() on an unknown, expired or deleted sliver (by explicit URN) shall 
        # result in an error (e.g. SEARCHFAILED, EXPIRED, or ERROR) (unless geni_best_effort 
        # is true, in which case the method may succeed and return a geni_error for each 
        # sliver that failed). Attempting to Delete a slice (no slivers identified) with 
        # no current slivers at this aggregate may return an empty list of slivers, may 
        # return a list of previous slivers that have since been deleted, or may even 
        # return an error (e.g. SEARCHFAILED or `EXPIRED); details are aggregate specific.
        
        try:
            result = self.__delegate.delete(urns)
        # Return error codes depending on given exception
        except DeleteError as e:
            return self.error_result(self.__geni_exception_manager.ERROR, e)
        except ShutDown as e:
            return self.error_result(self.__geni_exception_manager.UNAVAILABLE, e)
        
        return self.success_result(result)
    
    def PerformOperationalAction(self, urns=list(), credentials=list(), action=None, options=dict()):
        
        try:
            self.__credential_manager.validate_for("provision", credentials)
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.FORBIDDEN, e)
        
        actions = ['geni_start', 'geni_restart', 'geni_stop']
        if action not in actions:
            return self.error_result(self.__geni_exception_manager.UNSUPPORTED, "Unsupported Action")
        
        if options.get('geni_best_effort'):
            best_effort = True
        else:
            best_effort = False
        
        try:
            result = self.__delegate.perform_operational_action(urns, action, best_effort)
        except PerformOperationalStateError as e:
            return self.error_result(self.__geni_exception_manager.BADARGS, e)
        
        return self.success_result(action)
     
    def Status(self, urns=list(), credentials=list(), options=dict()):
        try:
            self.__credential_manager.validate_for("Status", credentials)
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.FORBIDDEN, e)
        try:
            result = self.__delegate.status(urns)
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.ERROR, e)
            
        
        return self.success_result(result)
    
    def Renew(self, urns=list(), credentials=list(), expiration_time=None, options=dict()):
        try:
            self.__credential_manager.validate_for("Status", credentials)
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.FORBIDDEN, e)
        
        expiration = self.get_expiration()
        now = datetime.datetime.utcnow()
        
        if 'geni_extend_alap' in options and options['geni_extend_alap']:
            if expiration < expiration_time:
                expiration= expiration_time
        
        if expiration < expiration_time:
            # Fail the call, the requested expiration exceeds the slice expir.
            msg = (("Out of range: Expiration %s is out of range"
                   + " (past last credential expiration of %s).")
                   % (expiration_time, expiration))
            return self.error_result(self.__geni_exception_manager.OUTOFRANGE, msg)
        elif expiration_time < now:
            msg = (("Out of range: Expiration %s is out of range"
                   + " (prior to now %s).")
                   % (expiration_time, now.isoformat()))
            print "What I am doing?"
            return self.error_result(self.__geni_exception_manager.OUTOFRANGE, msg)
        else:
            result = self.__delegate.renew(urns, expiration)
        
        return self.success_result(result)
    
    def ShutDown(self, urns=list(), credentials=list(), options=list()):
        return self.error_result(self.__geni_exception_manager.FORBIDDEN, "ShutDown Method is only available for the AM administrators")
    
    def __get_max_expiration(self):
        six_months = datetime.timedelta(weeks = 6 * 4) #6 months
        return six_months
    
    # Helper functions
    def get_expiration(self):
        ''' Max duration is a datetime.timedelta Object'''
        now = datetime.datetime.utcnow()
        expires = self.__credential_manager.get_expiration_list()
        max_duration = self.__get_max_expiration()
        if max_duration:
            expires.append(now + max_duration)
        return min(expires)
    
    def success_result(self, value):
        return self.build_property_list(0, value=value)
    
    def error_result(self, code, output):
        return self.build_property_list(code, output=output)
    
    def build_property_list(self, geni_code, value=None, output=None):
        result = {}
        result["code"] = {'geni_code': geni_code}
        # Non-zero geni_code implies error: output is required, value is optional
        if geni_code:
            result["output"] = output
            if value:
                result["value"] = value
        # Zero geni_code implies success: value is required, output is optional
        else:
            result["value"] = value
        return result
    
    def get_delegate(self):
        return self.__delegate
    
    def get_credential_manager(self):
        return self.__credential_manager
    
    def get_rspec_manager(self):
        return self.__rspec_manager
    
    def get_geni_exception_manager(self):
        return self.__geni_exception_manager
    
    def set_delegate(self, value):
        self.__delegate = value
    
    def set_credential_manager(self, value):
        self.__credential_manager = value
    
    def set_rspec_manager(self, value):
        self.__rspec_manager = value
    
    def set_geni_exception_manager(self, value):
        self.__geni_exception_manager = value
