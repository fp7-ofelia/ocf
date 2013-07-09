from expedient.clearinghouse.aggregate.models import *
import uuid
from expedient.clearinghouse.monitoring.AggregateMonitoringThread import AggregateMonitoringThread
from expedient.clearinghouse.monitoring.SessionMonitoringThread import SessionMonitoringThread
import time
import threading
from expedient.clearinghouse.settings import MONITORING_INTERVAL 
from vt_plugin.models import *

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
    def __monitorAggregates():

        for aggregate in Aggregate.objects.all():
            #aggregate = aggregate.as_leaf_class()
	    print "I am going to monitor: "+aggregate.name
            AggregateMonitoringThread.monitorAggregateInNewThread(aggregate)

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
            print "MONITORING AGGREGATES..."
            BackgroundMonitor.__monitorAggregates()
            if sessionMultipler % SESSION_MULTIPLIER == 0:
                  sessionMultipler = 0
                  BackgroundMonitor.__monitorSessions()
            else:
                sessionMultipler +=1
            time.sleep(MONITORING_INTERVAL)	
