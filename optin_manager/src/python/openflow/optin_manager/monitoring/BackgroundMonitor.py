#from openflow.optin_manager.monitoring.SessionMonitoringThread import SessionMonitoringThread
from SessionMonitoringThread import SessionMonitoringThread
import time
import threading
#from vt_manager.settings.settingsLoader import MONITORING_INTERVAL 
from django.conf import settings

'''
author:msune
Monitoring thread implementation
'''


SESSION_MULTIPLIER = 5 


class BackgroundMonitor():
    
    '''
    Several monitoring actions 
    '''

    @staticmethod
    def __monitorSessions():
        print "CBA background monitor callin monitorSessionInNewThread"
        SessionMonitoringThread.monitorSessionInNewThread()

    @staticmethod
    def monitor():
        print "CBA background monitor session"
        sessionMultipler = 0
        while True:
            print "CBA background monitor sessionMultipler: ", sessionMultipler
            if sessionMultipler % SESSION_MULTIPLIER == 0:
                      sessionMultipler = 0
                      print "CBA background monitor call monitorSessions"
                      BackgroundMonitor.__monitorSessions()
#            else:
#                sessionMultipler +=1
#                print "CBA background monitor increase multipler"
            sessionMultipler +=1
            print "CBA background monitor sleep interval: ", settings.MONITORING_INTERVAL
            time.sleep(settings.MONITORING_INTERVAL)	
            print "CBA background monitor end sleep"
