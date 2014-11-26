from openflow.optin_manager.monitoring.util.expiration_manager import ExpirationManager
import threading
import time

class BackgroundReservationMonitoring():
      
    period = 3600/4 * 3  #45 minutes in seconds
   
    @staticmethod      
    def monitor():
        while True:
            ExpirationManager.launch_reservation_queue()
            time.sleep(BackgroundReservationMonitoring.period)
