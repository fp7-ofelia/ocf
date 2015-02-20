from ambase.src.abstract.classes.handlerbase import HandlerBase
from ambase.src.ambase.exceptions import SliceAlreadyExists
from ambase.src.ambase.exceptions import AllocationError
from ambase.src.ambase.exceptions import ProvisionError
from ambase.src.ambase.exceptions import DeleteError
from ambase.src.ambase.exceptions import Shutdown
from ambase.src.ambase.exceptions import PerformOperationalStateError

import base64
import datetime
import dateutil.parser
import re
import zlib

class GeniV3Handler(HandlerBase):
       
    def __init__(self):
        self.__delegate = None
        self.__credential_manager = None
        self.__rspec_manager = None
        self.__geni_exception_manager = None
        self.__config = None
    
    def GetVersion(self, options=dict()):
        try:
            value = self.__delegate.get_version()
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.ERROR, e) 
        return self.success_result(result=value)

    def ListResources(self, credentials=list(), options=dict()):
        # Credential validation
        try:
            self.__credential_manager.validate_for("ListResources", credentials)
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.FORBIDDEN, e)
        # Required options validation
        if not options.has_key("geni_rspec_version"):
            return self.error_result(self.__geni_exception_manager.BADARGS, "Bad Arguments: option geni_rspec_version required in options")
        required_options = set(["type", "version"])
        option_list = set(options["geni_rspec_version"].keys())
        if not required_options.issubset(option_list):
            return self.error_result(self.__geni_exception_manager.BADARGS, "Bad Arguments: option geni_rspec_version does not have a version, type or geni_rspec_version fields.")
        
        # Allow only the rspec versions advertised in GetVersion
        user_geni_rspec_version = str(options.get("geni_rspec_version").get("version")).lower()
        # TODO: Retrieve 'am_geni_rspec_version' and 'am_geni_rspec_type' as a list of values; not just the first one!
        am_geni_rspec_version = str(self.__delegate.get_version().get("geni_ad_rspec_versions")[0].get("version")).lower()
        user_geni_rspec_type = str(options.get("geni_rspec_version").get("type")).lower()
        am_geni_rspec_type = str(self.__delegate.get_version().get("geni_ad_rspec_versions")[0].get("type")).lower()
        if user_geni_rspec_version != am_geni_rspec_version or user_geni_rspec_type != am_geni_rspec_type:
            return self.error_result(self.__geni_exception_manager.BADVERSION, "Bad Version: option geni_rspec_version defines an invalid version, type or geni_rspec_version value.")
        # Retrieving raw resources
        geni_available = options.get("geni_available", False)
        resources = self.__delegate.list_resources(geni_available)
        # Crafting resources into RSpec
        output = self.__rspec_manager.compose_advertisement(resources)
        # Preparing the output
        if options.get("geni_compressed", False):
            output = base64.b64encode(zlib.compress(output))
        return self.listresources_success_result(output)
        
    def Describe(self, urns=dict(),credentials=dict(),options=dict()):
        # Credential validation
        try:
            self.__credential_manager.validate_for("Describe", credentials)
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.FORBIDDEN, e)
        if not options.get("geni_rspec_version"):
            return self.error_result(self.__geni_exception_manager.BADARGS, "Bad Arguments: option geni_rspec_version does not have a version, type or geni_rspec_version fields.")
        # Options validation
        required_options = set(["type", "version"])
        option_list = set(options["geni_rspec_version"].keys())
        if not required_options.issubset(option_list):
            return self.error_result(self.__geni_exception_manager.BADARGS, "Bad Arguments: option geni_rspec_version does not have a version, type or geni_rspec_version fields.")

        # Retrieving slivers to manifest
        slivers = self.__delegate.describe(urns)
        
        # Crafting slivers to manifest RSpec
        output = self.__rspec_manager.compose_manifest(slivers)
        
        if options.get("geni_compressed", False):
            output = base64.b64encode(zlib.compress(output))

        if slivers:
            # Only act if there is a result
            if not type(slivers) == list:
                slivers = [slivers]
            try:
                slice_urn = slivers[0].get_sliver().get_slice_urn()
            except:
                slice_urn = slivers[0].get_slice_urn()
        else:
            slice_urn = urns[0]
        
        return self.success_result(output, slivers, slice_urn)

    def Allocate(self, slice_urn="", credentials=list(), rspec="", options=dict()):
        # Credential validation
        try:
            creds = self.__credential_manager.validate_for("Allocate", credentials)
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.FORBIDDEN, e)
        reservation = self.__rspec_manager.parse_request(rspec)
        # expiration == self.__get_expiration(creds)
        # First is datetime, Second is RFC3339
        expiration = self.__credential_manager.get_slice_expiration(creds)
        # It is possible to request for sliver expiration time < credentials expiration time
        if "geni_end_time" in options:
            expiration = min(self.__get_expiration(creds), options["geni_end_time"])
        users = self.__get_users_pubkeys(creds)
        try:
            allocated_slivers = self.__delegate.reserve(slice_urn, reservation, expiration, users)
        except SliceAlreadyExists as e:
            return self.error_result(self.__geni_exception_manager.ALREADYEXISTS, e)
        except AllocationError as e:
            return self.error_result(self.__geni_exception_manager.ERROR, e)
        
        manifest = self.__rspec_manager.compose_manifest(allocated_slivers)
        if not type(allocated_slivers) == list:
            allocated_slivers = [allocated_slivers]

        return self.success_result(manifest, allocated_slivers)
        
    def Provision(self, urns=list(), credentials=list(), options=dict()):
        # Credential validation
        try:
            creds = self.__credential_manager.validate_for("Provision", credentials)
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.FORBIDDEN, e)
        
        #expiration = self.__get_expiration()
        expiration = self.__credential_manager.get_slice_expiration(creds)
        if "geni_end_time" in options:
            #XXX I know, theory says that should be the minimum, but I don't trust the credentials expiration, yet
            expiration = max(self.__get_expiration(creds), options["geni_end_time"])
        if not "geni_users" in options:
            users = self.__get_users_pubkeys(creds)
        else:
            users = self.__format_geni_users(options["geni_users"])
        if not options.get("geni_rspec_version"):
            return self.error_result(self.__geni_exception_manager.BADARGS, "Bad Arguments: option geni_rspec_version does not have a version, type or geni_rspec_version fields.")
        # Options validation
        required_options = set(["type", "version"])
        option_list = set(options["geni_rspec_version"].keys())
        if not required_options.issubset(option_list):
            return self.error_result(self.__geni_exception_manager.BADARGS, "Bad Arguments: option geni_rspec_version does not have a version, type or geni_rspec_version fields.")
        # geni_best_effort filled up when present
        geni_best_effort = options.get("geni_best_effort", False)
        try:
            slivers = self.__delegate.create(urns, expiration, users, geni_best_effort)
        except ProvisionError as e:
            if "NO ALLOCATION FOUND" in str(e).upper():
                return self.error_result(self.__geni_exception_manager.SEARCHFAILED, str(e))
            elif "RE-PROVISIONING" in str(e).upper():
                return self.error_result(self.__geni_exception_manager.EXPIRED, str(e))
            else:
                return self.error_result(self.__geni_exception_manager.ERROR, str(e))
        
        manifest = self.__rspec_manager.compose_manifest(slivers)
        if not type(slivers) == list:
            slivers = [slivers]
        return self.success_result(manifest, slivers)
    
    def Delete(self, urns=list(), credentials=list(), options=dict()):
        # Credential validation
        try:
            creds = self.__credential_manager.validate_for("Delete", credentials)
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.FORBIDDEN, e)
        
        # Calling Delete() on an unknown, expired or deleted sliver (by explicit URN) shall 
        # result in an error (e.g. SEARCHFAILED, EXPIRED, or ERROR) (unless geni_best_effort 
        # is true, in which case the method may succeed and return a geni_error for each 
        # sliver that failed). Attempting to Delete a slice (no slivers identified) with 
        # no current slivers at this aggregate may return an empty list of slivers, may 
        # return a list of previous slivers that have since been deleted, or may even 
        # return an error (e.g. SEARCHFAILED or `EXPIRED); details are aggregate specific.
        
        # geni_best_effort filled up when present
        geni_best_effort = options.get("geni_best_effort", False)
        try:
            result = self.__delegate.delete(urns, geni_best_effort)
        # Return error codes depending on given exception
        except DeleteError as e:
            return self.error_result(self.__geni_exception_manager.ERROR, e)
        
        return self.delete_success_result(result)
    
    def PerformOperationalAction(self, urns=list(), credentials=list(), action=None, options=dict()):
        # Credential validation
        try:
            creds = self.__credential_manager.validate_for("PerformOperationalAction", credentials)
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.FORBIDDEN, e)

        actions = ["geni_start", "geni_restart", "geni_stop", "geni_update_users",
                        "geni_updating_users_cancel", "geni_console_url"]
        # TODO Add geni_updating_users_cancel
        if action not in actions:
            return self.error_result(self.__geni_exception_manager.UNSUPPORTED, "Unsupported Action")

        if options.get("geni_best_effort"):
            best_effort = True
        else:
            best_effort = False
        
        try:
            result = self.__delegate.perform_operational_action(urns, action, best_effort, options) 
        except PerformOperationalStateError as e:
            if "BUSY" in str(e).upper():
                return self.error_result(self.__geni_exception_manager.BUSY, e)
            elif "REFUSED" in str(e).upper():
                return self.error_result(self.__geni_exception_manager.REFUSED, e)
            else:
                return self.error_result(self.__geni_exception_manager.BADARGS, e)
        
        # Format undefined for this option, since it is "not fully implemented"        
        if action == "geni_console_url":
            return result
        
        return self.success_result(slivers_direct=result)
     
    def Status(self, urns=list(), credentials=list(), options=dict()):
        # Credential validation
        try:
            creds = self.__credential_manager.validate_for("Status", credentials)
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.FORBIDDEN, e)
        
        #expiration = self.__credential_manager.get_slice_expiration(creds)
        
        try:
            result = self.__delegate.status(urns)
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.ERROR, e)
       
        if result:
            # Only act if there is a result
            if not type(result) == list:
                result = [result]
            try:
               
               slice_urn = result[0].get_sliver().get_slice_urn()
            except:
               slice_urn = result[0].get_slice_urn()
        else:
            slice_urn = urns[0]
        return self.success_result(slivers=result, slice_urn=slice_urn)
    
    def Renew(self, urns=list(), credentials=list(), expiration_time=None, options=dict()):
        # Credential validation
        try:
            creds = self.__credential_manager.validate_for("Renew", credentials)
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.FORBIDDEN, e)
        slice_expiration = self.__credential_manager.get_slice_expiration(creds)
        try:
            slice_expiration = self.__rfc3339_to_datetime(slice_expiration)
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.SEARCHFAILED, e)
        # Format dates to expected output
        try:
            expiration_time = self.__rfc3339_to_datetime(expiration_time)
        except Exception as e:
            return self.error_result(self.__geni_exception_manager.ERROR, e)
        now = datetime.datetime.utcnow()
        # NOTE: Possibly existing on GCF, but not on GENIv3 API. Using it here, though
        if "geni_extend_alap" in options and options["geni_extend_alap"]:
            if slice_expiration < expiration_time:
                slice_expiration = expiration_time
        # If slice already expired & user tries to extend...
        if slice_expiration < expiration_time:
            # Fail the call, the requested expiration exceeds the slice expir.
            msg = "Expired slice or slivers: Requested expiration %s exceeds sliver expiration %s" \
                   % (expiration_time, slice_expiration)
            return self.error_result(self.__geni_exception_manager.EXPIRED, msg)
        # If user tries to extend to a past date...
        elif expiration_time < now:
            msg = "Expired slice or slivers: Requested expiration %s is in the past (current time: %s)" \
                   % (expiration_time, now.strftime("%Y-%m-%d %H:%M:%S.%f"))
            return self.error_result(self.__geni_exception_manager.ERROR, msg)
        # When requested expiration time is less than the slice expiration and a valid expiration date, serve
        else:
            # Check options and perform call to delegate
            geni_best_effort = options.get("geni_best_effort", False)
            try:
                result = self.__delegate.renew(urns, expiration_time, geni_best_effort)
            except Exception as e:
#                if "NOT FOUND" in str(e).upper():
                return self.error_result(self.__geni_exception_manager.SEARCHFAILED, str(e))
        return self.success_result(slivers_direct=result)
    
    def Shutdown(self, slice_urn="", credentials=list(), options=dict()):
        return self.error_result(self.__geni_exception_manager.FORBIDDEN, "Shutdown method is only available for the AM administrators")
    
    def __get_max_expiration(self):
        #six_months = datetime.timedelta(weeks = 6 * 4) #6 months
        one_hour = datetime.timedelta(hours = 1)
        return one_hour
    
    # Helper methods
    def __get_expiration(self, creds):
        now = datetime.datetime.utcnow()
        expires = self.__credential_manager.get_expiration_list(creds)
        # max_duration is a datetime.timedelta object
        max_duration = self.__get_max_expiration()
        if max_duration:
            expires.append(now + max_duration)
        return self.__datetime_to_rfc3339(min(expires))
    
    def __datetime_to_rfc3339(self, date):
        """
        Returns a datetime object that is formatted according to RFC3339.
        """
        try:
            # Hint: use "strict_rfc3339" package for validation: strict_rfc3339.validate_rfc3339(...)
            # May also be computed as date.replace(...).isoformat("T")
            formatted_date = date.replace(tzinfo=dateutil.tz.tzutc()).strftime("%Y-%m-%d %H:%M:%S.%f").replace(" ", "T")+"Z"
        except:
            try:
                formatted_date = date.replace(tzinfo=dateutil.tz.tzutc()).strftime("%Y-%m-%d %H:%M:%S").replace(" ", "T")+"Z"
            except:
                formatted_date = date
        return formatted_date
    
    def __rfc3339_to_datetime(self, date):
        """
        Returns a datetime object from an input string formatted according to RFC3339.
        """
        try:
            # Removes everything after a "+" or a "."
            #date_form = re.sub(r'[\+|\.].+', "", date)
            # Removes everything after a "+"
            date_form = re.sub(r'[\+].+', "", date)
            try:
                formatted_date = datetime.datetime.strptime(date_form.replace("T"," "), "%Y-%m-%d %H:%M:%S.%f")
                #formatted_date = datetime.datetime.strptime(date[:-1].replace("T"," "), "%Y-%m-%d %H:%M:%S")
            except:
                formatted_date = datetime.datetime.strptime(date_form.replace("T"," "), "%Y-%m-%d %H:%M:%S")
        except:
            formatted_date = date
        return formatted_date
    
    def delete_success_result(self, slivers):
        value = list()
        
        for sliver in slivers:
            try:
                sliver = sliver.get_sliver()
                error_msg = sliver.get_error_message()
            except:
                sliver = sliver
                error_msg = None
            sliver_struct = dict()
            sliver_struct["geni_sliver_urn"] = sliver.get_urn()
            sliver_struct["geni_allocation_status"] =  sliver.get_allocation_status()
            sliver_struct["geni_expires"] = sliver.get_expiration()
            if not error_msg == None:
                sliver_struct["geni_error"] = error_msg
            value.append(sliver_struct)
        return self.build_property_list(self.__geni_exception_manager.SUCCESS, value=value)
    
    def listresources_success_result(self, rspec):
        return self.build_property_list(self.__geni_exception_manager.SUCCESS, value=rspec)

    def success_result(self, rspec=None, slivers=[], slice_urn=None, slivers_direct=list(), result=None):
        """
        Prepares "value" struct.
        """
        if slivers_direct:
            value = list()
            for sliver in slivers_direct:
                geni_sliver_special_struct = self.__get_geni_sliver_structure(sliver)
                value.append(geni_sliver_special_struct)
        elif result != None:
            value = result
        else:    
            value = dict()
            if rspec:
                value["geni_rspec"] = rspec
            if slice_urn:
                value["geni_urn"] = slice_urn
            if slivers:
                value["geni_slivers"] = list()
                for sliver in slivers:
                    geni_sliver_struct = self.__get_geni_sliver_structure(sliver)
                    value["geni_slivers"].append(geni_sliver_struct)
        return self.build_property_list(self.__geni_exception_manager.SUCCESS, value=value)
    
    def error_result(self, code, output):
        return self.build_property_list(code, output=str(output))
    
    def build_property_list(self, geni_code, value=None, output=None):
        result = {}
        result["geni_api"] = self.__config.GENI_API_VERSION
        result["code"] = {"geni_code": geni_code}
        if self.__config:
            if self.__config.AM_TYPE:
                result["code"]["am_type"] = self.__config.AM_TYPE
            if self.__config.AM_CODE_VERSION:
                result["code"]["am_code"] = self.__config.AM_CODE_VERSION
        # Non-zero geni_code implies error: output is required, value is optional
        if geni_code:
            result["output"] = output
            result["value"] = ""
            if value:
                result["value"] = value
        # Zero geni_code implies success: value is required, output is optional
        else:
            result["value"] = value
        return result
    
    def __get_geni_sliver_structure(self, resource):
        try:
            sliver = resource.get_sliver()
            error_message = resource.get_error_message()
        except:
            sliver = resource
            error_message = None
        sliver_struct = dict()
        sliver_struct["geni_sliver_urn"] = sliver.get_urn()
        sliver_struct["geni_allocation_status"] =  sliver.get_allocation_status()
        sliver_struct["geni_expires"] = self.__datetime_to_rfc3339(sliver.get_expiration())
        sliver_struct["geni_operational_status"] = sliver.get_operational_status()
        if error_message:
            sliver_struct["geni_error"] = error_message
        return sliver_struct

    def __get_users_pubkeys(self, creds):
        users = list()
        for cred in creds:
            user = dict()
            user_gid = cred.get_gid_caller()
            user["name"] = user_gid.get_urn()
            user["keys"] = user_gid.get_pubkey().get_pubkey_string()
            if not type(user["keys"]) == list:
                user["keys"] = [user["keys"]]
            users.append(user)
        return users

    def __format_geni_users(self, geni_users):
        users = list()
        for user in geni_users:
            name = user['urn']
            users.append({'name':name, 'keys':user['keys']})
        return user
 
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
    
    def set_config(self, value):
        self.__config = value
