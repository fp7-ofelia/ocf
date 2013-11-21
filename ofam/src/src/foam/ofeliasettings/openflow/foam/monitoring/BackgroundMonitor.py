from openflow.optin_manager.monitoring.SessionMonitoringThread import SessionMonitoringThread
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
        SessionMonitoringThread.monitorSessionInNewThread()

    @staticmethod
    def monitor():
        sessionMultipler = 0
        while True:
            if sessionMultipler % SESSION_MULTIPLIER == 0:
                      sessionMultipler = 0
                      BackgroundMonitor.__monitorSessions()
            else:
                sessionMultipler +=1
            time.sleep(settings.MONITORING_INTERVAL)	
