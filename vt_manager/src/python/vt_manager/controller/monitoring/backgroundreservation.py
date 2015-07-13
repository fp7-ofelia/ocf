from vt_manager.models.reservation import Reservation 
from vt_manager.models.VirtualMachine import VirtualMachine
from datetime import datetime
import threading
import time


class BackgroundReservationMonitoring(threading.Thread):
      
    period = 3600  #seconds
   
    def __init__(self):
        threading.Thread.__init__(self)
        self.period = 900 
        
    def monitor(self):
        self.start()
     
    def run(self):
        while True:
            print "Background VM Reservation Monitoring Thread starting...\n"
            reservations = Reservation.objects.all()
            try:
                for r in reservations:
                    exp_date = r.get_valid_until().replace("Z", "").replace("T", " ")
                    try:
                        exp_time = datetime.strptime(exp_date, '%Y-%m-%d %H:%M:%S.%f')
                    except:
                        exp_time = datetime.strptime(exp_date, '%Y-%m-%d %H:%M:%S')
                    if exp_time < datetime.utcnow():
                        print "Deleting reservation (name=%s) upon expiration=%s" % (r.name, r.valid_until)
                        r.delete()
            except Exception as e:
                print "Reservation Monitoring failed, cause:", str(e)
            
            time.sleep(self.period)
