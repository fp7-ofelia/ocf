from vt_manager.models.reservation import Reservation 
from datetime import datetime
import threading


class BackgroundReservationMonitoring(threading.Thread):
      
    period = 3600  #seconds
   
    def __init__(self):
        threading.Thread.__init__(self)
        self.period = 900 
        
    def monitor():
        self.start()
     
    def run():
        while True:
            reservations = Reservation.objects.all()
            try:
                for r in reservations:
                    time = datetime.strptime(r.get_valid_until, '%Y-%m-%d %H:%M:%S.%f')
                    if time < datetime.utcnow():
                        r.delete
            except Exception as e:
                print "Reservation Monitoring failed, cause:", srt(e)
            
            time.sleep(self.period)
