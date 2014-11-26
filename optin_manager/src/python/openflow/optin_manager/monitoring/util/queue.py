import threading 
import time 
import datetime

class Queue(threading.Thread):

    def __init__(self, exp_buffer=list(), ttl =3600/4*3):
        threading.Thread.__init__(self)
        self.exp_buffer = exp_buffer
        self.ttl = ttl
        self.slept_time = 0

    def run(self):
        for exp, method, params in self.exp_buffer:
            sleep_time = self.get_time_difference(exp)
            if sleep_time > 0:
                time.sleep(sleep_time)
                self.slept_time += sleep_time
            method(**params)
            if self.ttl <= self.slept_time:
                self.exp_buffer = list()
                break

    

    def delete_expired(self, res, fss, exp):
        try:
            #from openflow.optin_manager.opts.models import Reservation
            #from openflow optin_manager.opts.models import ReservationFlowSpace
            print "res", res
            print "fss", fss
            print "exp", exp 
            if exp >= int(datetime.datetime.strptime(res.expiration.split(".")[0], "%Y-%m-%d %H:%M:%S").strftime("%s")): #Avoiding last-minute renews
                fss.delete()
                res.delete()
        except Exception as e:
            import traceback
            print traceback.print_exc() 
        
    def get_time_difference(self, exp):
        #expiration = datetime.datetime.strftime(str(exp2.split(".")[0]),"%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.utcnow()
        return  exp - int(now.strftime("%s")) 

    
