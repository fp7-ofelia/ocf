import base64
import zlib
import datetime

from src.ambase.exceptions import SliceAlreadyExists
from src.ambase.exceptions import AllocationError
from src.ambase.exceptions import ProvisionError
from src.ambase.exceptions import DeleteError
from src.ambase.exceptions import ShutDown
from src.ambase.exceptions import UnsupportedState
from src.ambase.exceptions import PerformOperationalStateError

class GeniV3Handler:
    
    def __init__(self):
        self.__delegate= None
        self.__credential_manager = None
        self.__rspec_manager = None
        self.__geni_exception_manager = None

    def GetVersion(self, options=dict()):
        version=dict()
        return self.success_result(version)

    def ListResources(self, credentials=list(), options=dict()):
        
        #Credential Validation
        try:
            self.__credential_manager.validate_for("list_resources", credentials)
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.FORBIDDEN)
        
        #Options Validation
        required_options = set(['geni_rspec_version','type', 'version'])
        option_list = set(options['geni_rspec_version'].keys())
        if not required_options.issubset(option_list):
            return self.error_result(self.__geni_exception_manager.BADARGS, 'Bad Arguments: option geni_rspec_version does not have a version, type or geni_rspec_version fields.')
        
        #Retrieving RAW resources
        geni_available = False
        if options.get('geni_available'):
            if geni_available:
                geni_available = True
        resources = self.__delegate.list_resources(geni_available)
        
        #Crafting resources into RSpec
        output = self.__rspec_manager.advertise_resources(resources)
        
        
        #Preparing the output
        if 'geni_compressed' in options and options['geni_compressed']:
            output = base64.b64encode(zlib.compress(output))
            
        return self.success_result(output)
        
    def Describe(self, urns=dict(),credentials=dict(),options=dict()):
        
        #Credential Validation
        try:
            self.__credential_manager.validate_for("describe", credentials)
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.FORBIDDEN)
        
        #Options Validation
        required_options = set(['geni_rspec_version','type', 'version'])
        option_list = set(options['geni_rspec_version'].keys())
        if not required_options.issubset(option_list):
            return self.error_result(self.__geni_exception_manager.BADARGS, 'Bad Arguments: option geni_rspec_version does not have a version, type or geni_rspec_version fields.')

        #Retrieving Slivers to manifest
        slivers = self.__delegate.describe(urns)
        
        #crafting slivers to manifest RSpec
        output = self.__rspec_manager.manifest_slivers(slivers)
        
        if 'geni_compressed' in options and options['geni_compressed']:
            output = base64.b64encode(zlib.compress(output))
            
        return self.success_result(output)

    def Allocate(self, slice_urn="", credentials=list(), rspec="", options=dict()):
        #Credential Validation
        try:
            self.__credential_manager.validate_for("allocate", credentials)
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.FORBIDDEN)
        
        am = self.__rspec_manager.parse_request()
        expiration = self.min_expiration()
        try:
            allocated_slivers = self.__delegate.allocate(slice_urn, am, expiration)    
        except SliceAlreadyExists:
            return self.error_result(self.__geni_exception_manager.ALREADYEXISTs)
        except AllocationError:
            return self.error_result(self.__geni_exception_manager.ERROR)

        manifest = self.__rspec_manager.manifest_resources()
        
        return self.success_result(manifest)
        
    def Provision(self, urns=list(), credentials=list(), options=dict()):
        try:
            self.__credential_manager.validate_for("provision", credentials)
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.FORBIDDEN)
         
        expiration = self.min_expiration()
        
        #Options Validation
        required_options = set(['geni_rspec_version','type', 'version'])
        option_list = set(options['geni_rspec_version'].keys())
        if not required_options.issubset(option_list):
            return self.error_result(self.__geni_exception_manager.BADARGS, 'Bad Arguments: option geni_rspec_version does not have a version, type or geni_rspec_version fields.')

        try:
            slivers = self.__delegate.provision(urns)
        except ProvisionError as e:
            self.error_result(self.__geni_exception_Manager.ERROR, e, am_code)
        
        manifest = self.__rspec_manager.manifest_rspec(slivers)
        
        return self.successResult(manifest)
    
    def Delete(self, urns=list(), credentials=list(), options=dict()):
        
        try:
            self.__credential_manager.validate_for("provision", credentials)
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.FORBIDDEN)
        
        #TODO check if the slice is shutDown
        try:
            result = self.__delegate.delete(urns)
        except DeleteError as e:
            self.error_result(self.__geni_exception_manager.ERROR, e, am_code)
        except ShutDown as e:
            self.error_result(self.__geni_exception_manager.UNAVAILABLE)
        
        return self.success_result(result)  
    
    def PerformOperationalAction(self, urns=list(), credentials=list(), action=None, options=dict()):
        
        try:
            self.__credential_manager.validate_for("provision", credentials)
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.FORBIDDEN)
        
        actions = ['geni_start', 'geni_restart', 'geni_stop']
        if action not in actions:
            return self.error_result(self.__geni_exception_manager.UNSUPPORTED, output, am_code)
        
        if options.get('geni_best_effor'):
            best_effort = True
        else:
            best_effort = False
        
        try:
            result = self.__delegate.perform_operational_action(urns, action, best_effort)
        except UnsupportedState as e:
            return self.error_result(self.__geni_exception_manager.UNSUPPORTED, e, am_code)
        except PerformOperationalStateError as e:
            return self.error_message(self.__geni_exception_manager.UNSUPPORTED, e, am_code)
                
    def Status(self, urns=list(), credentials=list(), options=dict()):
        try:
            self.__credential_manager.validate_for("Status", credentials)
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.FORBIDDEN)
        
        result = self.__delegate.status(urns)
        
        return self.success_result(result)
        
    def Renew(self, urns=list(), credentials=list(), expiration_time=None, options=dict()):
        try:
            self.__credential_manager.validate_for("Status", credentials)
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.FORBIDDEN)
        
        expiration = self.min_expiration(credentials, self.max_lease)
        now = datetime.datetime.utcnow()
        
        if 'geni_extend_alap' in options and options['geni_extend_alap']:
            if expiration < expiration_time:
                expiration= expiration_time
        
        if expiration > expiration:
            # Fail the call, the requested expiration exceeds the slice expir.
            msg = (("Out of range: Expiration %s is out of range"
                   + " (past last credential expiration of %s).")
                   % (expiration_time, expiration))
            return self.errorResult(self.__geni_exception_manager.OUTOFRANGE, msg)
        elif expiration < now:
            msg = (("Out of range: Expiration %s is out of range"
                   + " (prior to now %s).")
                   % (expiration_time, now.isoformat()))

            return self.errorResult(self.__geni_exception_manager.OUT_OF_RANGE, msg)
        else:
            result = self.__delegate.renew(urns, expiration)
        
        return self.success_result(value)
        
    
    def ShutDown(self, urns=list(), credentials=list(), options=list()):
        return self.error_result(self.__geni_exception_manager.FORBIDDEN, output, am_code)
        
    #Helper Functions
    
    def success_result(self, value):
        code_dict = dict(geni_code=0, am_type=self._am_type, am_code=0)
        return dict(code=code_dict, value=value, output="")
    
    def error_result(self,code, output, am_code=None):
        code_dict = dict(geni_code=code, am_type=self._am_type)
        if am_code is not None:
            code_dict['am_code'] = am_code
        return dict(code=code_dict, value="", output=output)
    
    def min_expiration(self, creds, max_duration=None, requested=None):

        now = datetime.datetime.utcnow()
        expires = [self._naiveUTC(c.expiration) for c in creds]
        if max_duration:
            expires.append(now + max_duration)
        if requested:
            requested = self._naiveUTC(dateutil.parser.parse(str(requested), tzinfos=tzd))
            # Ignore requested time in the past.
            if requested > now:
                expires.append(self._naiveUTC(requested))
        return min(expires)