from expedient.clearinghouse.aggregate.models import *
import uuid
from expedient.clearinghouse.monitoring.AggregateMonitoringThread import AggregateMonitoringThread
import time
import threading
from expedient.clearinghouse.settings import MONITORING_INTERVAL 
from vt_plugin.models import *

'''
author:msune
Monitoring thread implementation
'''

class BackgroundMonitor():
    
    '''
    Updates server status
    '''
    @staticmethod
    def __monitorAggregates():

        for aggregate in Aggregate.objects.all():
            aggregate = aggregate.as_leaf_class()
            if isinstance(aggregate, VtPlugin):
                AggregateMonitoringThread.monitorAggregateInNewThread(aggregate)
        #Wait for threads
        for thread in threading.enumerate():
            if thread is not threading.currentThread():
                thread.join()

    @staticmethod
    def monitor():
        while True:
            print "MONITORING AGGREGATES..."
            BackgroundMonitor.__monitorAggregates()
            time.sleep(MONITORING_INTERVAL)	
