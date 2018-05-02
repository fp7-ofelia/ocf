
from datetime import datetime
from openflow.optin_manager.sfa.util.sfatime import utcparse, datetime_to_epoch
from openflow.optin_manager.sfa.models import ExpiringComponents
#from openflow.optin_manager.sfa.drivers.OFSfaDriver import OFSfaDriver

class ExpirationManager:

    @staticmethod
    def extend_expiration(slice_name,authority,time_extension):
        #time_extended = time_extension #FIXME: See how is processed the new expiration time
        try:
            exp_sl = ExpiringComponents.objects.get(slice=slice,authority=authority)
        except:
            raise Exception("Slice %s has already expired" %slice_name)
        exp_sl.extend_expiration(time_extension)


    @staticmethod
    def find_expired_slices():
        print "CBA find_expired_slices----------------------------------------------------------------"
        try:
            from openflow.optin_manager.sfa.drivers.OFSfaDriver import OFSfaDriver #Avoiding circular Deps
        except:
            pass
        slices = ExpiringComponents.objects.all()
        expired_components = list()
        for slice in slices:
            expiration_date = int(datetime_to_epoch(utcparse(slice.expires)))
            print("[OFAM] MONITORING BG / EXPIRATION MANAGER. expiration_date (" + str(expiration_date) + ") < current_date (" + str(datetime_to_epoch(utcparse(datetime.utcnow()))) + ")?: " + str(expiration_date <= int(datetime_to_epoch(utcparse(datetime.utcnow())))))
            if expiration_date <= int(datetime_to_epoch(utcparse(datetime.utcnow()))):
                try:
                    OFSfaDriver().crud_slice(slice.slice,slice.authority, 'delete_slice')
                except:
                    pass

    @staticmethod
    def launch_expired_fs():
        print "CBA launch expired fs-------------------------------------------------------------------"
        from openflow.optin_manager.opts.models import Experiment
        from openflow.optin_manager.opts.models import ExperimentFLowSpace
        from openflow.optin_manager.opts.models import ExpiringFlowSpaces
        from openflow.optin_manager.monitoring.util.queue import Queue
        
        expiration_buffer = list() 
        exps = Experiment.objects.exclude(slice_urn__isnull=True)
        print "CBA experiments: ", exps
        for exp in exps:
            try:
                print " "
                print " "
                print " "
                print "    CBA Experiment: ", exp
                # Attempt to retrieve expiring flowspaces for each experiment
                expiring_fs = ExpiringFlowSpaces.objects.get(slice_urn = exp.slice_urn)
                #print "    CBA launch expired fs expiring_flowspace: ", dir(expiring_fs)

                print "    CBA fecha           : ", expiring_fs.expiration
                date = expiring_fs.expiration
                formatted_date = ExpirationManager.convert_date_to_str(date)
                print "    CBA fecha modificada: ", formatted_date

                int_exp = ExpirationManager.convert_date_to_int(formatted_date)
                print "    CBA int_exp: ", int_exp

                params = {"urn": exp.slice_urn, "expiring_fs": expiring_fs, "expiration": int_exp}
                print "    CBA params: ", params
                # Delete related experiment
                ExpirationManager.delete_expired_experiment(params.get("urn"))
                # Delete related flowspaces
                method = ExpirationManager.delete_expired_flowspaces
                expiration_buffer.append((int_exp, method, params)) 
            except Exception as e:
                print "    CBA launch expired fs EXCEPTION: ", e
#                pass

        expiration_buffer.sort()
        print " "
        print " "
        print " "
        print "    CBA expiration_buffer: ", expiration_buffer
        q = Queue(expiration_buffer)
        print "    CBA encolar expiration buffer e iniciar"
        q.start()

    @staticmethod
    def launch_reservation_queue():
        from openflow.optin_manager.opts.models import Reservation
        from openflow.optin_manager.opts.models import ReservationFlowSpace
        from openflow.optin_manager.monitoring.util.queue import Queue
        expiration_buffer = list()
        reservations = Reservation.objects.all()
        for r in reservations:
            int_exp = int(datetime.strptime(r.expiration.split(".")[0], '%Y-%m-%d %H:%M:%S').strftime("%s"))
            print("\nlaunch_reservation_queue > delete reservation: ", r.__dict__)
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
            print("\ndelete_expired_reservations > check reservation for delete: ", str(reservation.__dict__))
            print("\ndelete_expired_reservations > expiration req? = ", str(expiration))
            print("\ndelete_expired_reservations > expiration? = ", str(int(datetime.strptime(reservation.expiration.split(".")[0], "%Y-%m-%d %H:%M:%S").strftime("%s"))))
            if expiration >= int(datetime.strptime(reservation.expiration.split(".")[0], "%Y-%m-%d %H:%M:%S").strftime("%s")): #Avoiding last-minute renews
                reservation_flowspaces.delete()
                reservation.delete()
        except:
            import traceback
            print(traceback.print_exc())

    @staticmethod
    def delete_expired_experiment(urn):
        try:
            print("\n\nDelete expired experiments**************************************************")
            from openflow.optin_manager.opts.models import Experiment

            date = expiring_fs.expiration
            print "Date: ", date
            formatted_date = ExpirationManager.convert_date_to_str(date)
            print "Formatted_date: ", formatted_date
            int_exp = ExpirationManager.convert_date_to_int(formatted_date)

            print "Experiment expiration: ", expiration
            print "Experiment   : ", int_exp
            if expiration >= int_exp: #Avoiding last-minute renews
                print("Experiment to be deleted")
                try:
                    experiments = Experiment.objects.filter(project_name=urn)
                    for exp in experiments:
                        exp.delete()
                except Exception as e:
                    print("[Exception] Delete expired experiment. Details: ", e)
            else:
                 print("Not removing experiment")
        except:
            import traceback
            print(traceback.print_exc())

    @staticmethod
    def delete_expired_flowspaces(urn, expiring_fs ,expiration):
        try:
            print "\n\nCBA delete expired flowspaces**************************************************"
            from openflow.optin_manager.geni.v3.utils.sliver import SliverUtils

            date = expiring_fs.expiration
            print "CBA date: ", date
            formatted_date = ExpirationManager.convert_date_to_str(date)
            print "CBA formatted_date: ", formatted_date
            int_exp = ExpirationManager.convert_date_to_int(formatted_date)

            print "CBA expiration: ", expiration
            print "CBA int_exp   : ", int_exp
            if expiration >= int_exp: #Avoiding last-minute renews
        #if expiration >= int(datetime.strptime(expiring_fs.expiration.split(".")[0], "%Y-%m-%d %H:%M:%S").strftime("%s")): #Avoiding last-minute renews
                print "CBA borramos fs"
                try:
                    SliverUtils.delete_of_sliver(urn)
                    expiring_fs.delete()
#            except:
#                pass
                except Exception as e:
                    print "CBA delete expired flowspaces EXCEPTION: ", e
            else:
                 print "CBA no borramos fs"
        except:
            import traceback
            print(traceback.print_exc())

    @staticmethod
    def convert_date_to_str(date):
        try:
            formatted_date = str(datetime.strptime(date.replace("T", " ").replace("Z", ""), "%Y-%m-%d %H:%M:%S"))
        except:
            formatted_date = str(date)
        return formatted_date

    @staticmethod
    def convert_date_to_int(date_str):
        try:
            int_exp = int(datetime.strptime(date_str.split(".")[0], '%Y-%m-%d %H:%M:%S').strftime("%s"))
        except:
            int_exp = int(date_str)
        return int_exp
