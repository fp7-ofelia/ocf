
from datetime import datetime
from openflow.optin_manager.sfa.util.sfatime import utcparse, datetime_to_epoch
from openflow.optin_manager.sfa.models import ExpiringComponents
#from openflow.optin_manager.sfa.drivers.OFSfaDriver import OFSfaDriver

class ExpirationManager:

    @staticmethod
    def extend_expiration(slice_name,authority,time_extension):
        time_extended = time_extension #FIXME: See how is processed the new expiration time
        try:
            exp_sl = ExpiringComponents.objects.get(slice=slice,authority=authority)
        except:
            raise Exception("Slice %s has already expired" %slice_name)
        exp_sl.extend_expiration(time_extension)


    @staticmethod
    def find_expired_slices():
        try:
            from openflow.optin_manager.sfa.drivers.OFSfaDriver import OFSfaDriver #Avoiding circular Deps
        except:
            pass
        slices = ExpiringComponets.objects.all()
        expired_components = list()
        for slice in slices:
            expiration_date = int(datetime_to_epoch(utcparse(slice.expires)))
            if expiration_date <= int(datetime_to_epoch(utcparse(datetime.utcnow()))):
                try:
                    OFSfaDriver().crud_slice(slice.slice,slice.authority, 'delete_slice')
                except:
                    pass
