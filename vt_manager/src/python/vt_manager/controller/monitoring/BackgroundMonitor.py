from vt_manager.models.VTServer import VTServer
import uuid
from vt_manager.controller.monitoring.AgentMonitoringThread import AgentMonitoringThread
import time
import threading
from vt_manager.settings import MONITORING_INTERVAL 

'''
author:msune
Monitoring thread implementation
'''

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
    def monitor():
        while True:
            print "Monitoring Servers Thread starting..."
            BackgroundMonitor.__monitorServers()
            time.sleep(MONITORING_INTERVAL)	
