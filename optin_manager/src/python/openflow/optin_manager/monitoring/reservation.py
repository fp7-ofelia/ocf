from openflow.optin_manager.monitoring.util.expiration_manager import ExpirationManager
import threading
import time

class BackgroundReservationMonitoring():
      
    period = 3600*3/4  #45 minutes in seconds
   
    @staticmethod      
    def monitor():
        while True:
            # Clean expired reservations
            ExpirationManager.launch_reservation_queue()
            # Clean expired flowspaces
            ExpirationManager.launch_expired_fs()
            # Others
            ExpirationManager.find_expired_slices()
            time.sleep(BackgroundReservationMonitoring.period)
