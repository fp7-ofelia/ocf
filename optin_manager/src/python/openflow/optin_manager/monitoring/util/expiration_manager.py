
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

    @staticmethod
    def launch_expired_fs():
        from openflow.optin_manager.opts.models import Experiment
        from openflow.optin_manager.opts.models import ExperimentFLowspace
        from openflow.optin_manager.opts.models import ExpiringFlowSpaces
        from openflow.optin_manager.monitoring.util.queue import Queue
        
        expiration_buffer = list() 
        exps = Experiment.objects.exclude(slice_urn__isnull=True)
        for exp in exps:
            expiring_fs = ExpiringFlowSpaces.objects.get(slice_urn = exp.slice_urn)
            int_exp = int(datetime.strptime(expiring_fs.expiration.split(".")[0], '%Y-%m-%d %H:%M:%S').strftime("%s")) 
            params = {"urn":exp.slice_urn, "expiring_fs":expiring_fs , "expiration":int_exp}
            method = ExpirationManager.delete_expired_flowspaces
            expiration_buffer.append((int_exp, method, params)) 

    @staticmethod
    def launch_reservation_queue():
        from openflow.optin_manager.opts.models import Reservation
        from openflow.optin_manager.opts.models import ReservationFlowSpace
        from openflow.optin_manager.monitoring.util.queue import Queue
        expiration_buffer = list()
        reservations = Reservation.objects.all()
        for r in reservations:
            int_exp = int(datetime.strptime(r.expiration.split(".")[0], '%Y-%m-%d %H:%M:%S').strftime("%s"))
            rfss = r.reservationflowspace_set.all()
            method = ExpirationManager.delete_expired_reservations
            params = {"reservation": r, "reservation_flowspaces":rfss, "expiration":int_exp}
            expiration_buffer.append((int_exp, method, params))
        
        expiration_buffer.sort()
        q = Queue(expiration_buffer)
        q.start() 
    
    @staticmethod         
    def delete_expired_reservations(reservation, reservation_flowspaces, expiration):
        try:
            #from openflow.optin_manager.opts.models import Reservation
            #from openflow optin_manager.opts.models import ReservationFlowSpace
            if expiration >= int(datetime.datetime.strptime(reservation.expiration.split(".")[0], "%Y-%m-%d %H:%M:%S").strftime("%s")): #Avoiding last-minute renews
                reservation_flowspaces.delete()
                reservation.delete()
        except Exception as e:
            import traceback
            print traceback.print_exc()

    @staticmethod
    def delete_expired_flowspaces(urn, expiring_fs ,expiration):
        from openflow.optin_manager.xmlrpc_server.models import FVServerProxy
        from openflow.optin_manager.opts.models import Experiment
        from openflow.optin_manager.opts.models import ExperimentFLowSpace
        from openflow.optin_manager.opts.models import UserOpts
        from openflow.optin_manager.opts.models import OptsFlowSpace
        from openflow.optin_manager.opts.models import MatchStruct
        from openflow.optin_manager.geni.v3.utils.sliver import SliverUtils
        from openflow.optin_manager.opts.models import ExpiringFlowSpaces
             
        if expiration >= int(datetime.datetime.strptime(expiring_fs.expiration.split(".")[0], "%Y-%m-%d %H:%M:%S").strftime("%s")): #Avoiding last-minute renews
            try:
                SliverUtils.delete_of_sliver(urn)
                exiring_fs.delete()
            except Exception as e:
                pass

