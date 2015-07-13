from vt_manager.models.reservation import Reservation 
from vt_manager.models.VirtualMachine import VirtualMachine
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
            print "Background VM Reservation Monitoring Thread starting..."
            reservations = Reservation.objects.all()
            try:
                for r in reservations:
                    time = datetime.strptime(r.get_valid_until, '%Y-%m-%d %H:%M:%S.%f')
                    if time < datetime.utcnow():
                        res_vm = VirtualMachine.objects.filter(uuid=r.uuid)
                        print "VM (name=%s, uuid=%s) has expired on time=%s. Proceeding to its deletion" % \
                                (res_vm.name, r.uuid, r.get_valid_until)
                        #if len(res_vm):
                        #    res_vm.delete()
                        r.delete
            except Exception as e:
                print "Reservation Monitoring failed, cause:", srt(e)
            
            time.sleep(self.period)
