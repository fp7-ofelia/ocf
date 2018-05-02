from openflow.optin_manager.sfa.openflow_utils.expiration_manager import ExpirationManager
import threading
import time

class BackgroundExpirationMonitoring(threading.Thread):
      
    period = 3600 * 6  #seconds
    #period = 1
   
    def __init__(self):
        threading.Thread.__init__(self)
        
    def monitor(self):
        self.start()
     
    def run(self):
        while True:
            # Clean expired flowspaces
            ExpirationManager.launch_expired_fs()
            # Others
            ExpirationManager.find_expired_slices()
            time.sleep(self.period)
