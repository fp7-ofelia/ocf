from openflow.optin_manager.monitoring.util.expiration_manager import ExpirationManager
import threading
import time

class BackgroundReservationMonitoring():
      
    period = 3600*3/4  #45 minutes in seconds
    #period = 30
   
    @staticmethod      
    def monitor():
        while True:
            # Clean expired reservations
#            print "CBA reservation monitor launch reservation queue"
            ExpirationManager.launch_reservation_queue()
            # Clean expired flowspaces
#            print "CBA reservation monitor launch expired flowspace"
            ExpirationManager.launch_expired_fs()
            # Others
#            print "CBA reservation monitor launch expired slices"
            ExpirationManager.find_expired_slices()
#            print "CBA reservation monitor sleep 1 minute"
            time.sleep(BackgroundReservationMonitoring.period)
#            print "CBA reservation monitor end sleep"
