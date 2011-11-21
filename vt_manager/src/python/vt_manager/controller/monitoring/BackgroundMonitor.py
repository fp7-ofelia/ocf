from vt_manager.models.VTServer import VTServer
import uuid
from vt_manager.controller.monitoring.AgentMonitoringThread import AgentMonitoringThread
from vt_manager.controller.monitoring.SessionMonitoringThread import SessionMonitoringThread
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
    Updates server status
    '''
    @staticmethod
    def __monitorServers():

        for server in VTServer.objects.all():
            AgentMonitoringThread.monitorAgentInNewThread(server)
        #Wait for threads
        for thread in threading.enumerate():
            if thread is not threading.currentThread():
                thread.join()

    @staticmethod
    def __monitorSessions():
        SessionMonitoringThread.monitorSessionInNewThread()

    @staticmethod
    def monitor():
        sessionMultipler = 0
        while True:
            print "Monitoring Servers Thread starting..."
            BackgroundMonitor.__monitorServers()
            if sessionMultipler % SESSION_MULTIPLIER == 0:
                      sessionMultipler = 0
                      BackgroundMonitor.__monitorSessions()
            else:
                sessionMultipler +=1
            time.sleep(settings.MONITORING_INTERVAL)	
