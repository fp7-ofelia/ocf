from openflow.optin_manager.sfa.openflow_utils.expiration_manager import ExpirationManager
import threading
import time

class BackgroundExpirationMonitoring(threading.Thread):
      
    period = 3600*6  #seconds
   
    def __init__(self):
        threading.Thread.__init__(self)
        
    def monitor():
        self.start()
     
    def run():
        while True:
            ExpirationManager.find_expired_slices()
            time.sleep(self.period)
