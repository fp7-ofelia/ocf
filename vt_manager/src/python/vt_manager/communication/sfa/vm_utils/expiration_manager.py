from datetime import datetime
from vt_manager.communication.sfa.util.sfatime import utcparse, datetime_to_epoch
from vt_manager.models.expiring_components import ExpiringComponents
from vt_manager.communication.sfa.drivers.VTSfaDriver import VTSfaDriver

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
        slices = ExpiringComponets.objects.all()
        expired_components = list()
        for slice in slices:
            expiration_date = int(datetime_to_epoch(utcparse(slice.expires)))
            if expiration_date <= int(datetime_to_epoch(utcparse(datetime.utcnow()))):
                try:
                    VTSfaDriver().crud_slice(slice.slice,slice.authority, 'delete_slice')
                except:
                    pass

     

    
