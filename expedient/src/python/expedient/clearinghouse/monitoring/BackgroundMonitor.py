from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.clearinghouse.monitoring.AggregateMonitoringThread import AggregateMonitoringThread
from expedient.clearinghouse.monitoring.SessionMonitoringThread import SessionMonitoringThread
from expedient.clearinghouse.settings import MONITORING_INTERVAL 

import time
import threading

"""
author: msune, CarolinaFernandez
Monitoring thread implementation
"""

SESSION_MULTIPLIER = 5
AGGREGATE_OF_MULTIPLIER = 2

class BackgroundMonitor():
    
    """
    Updates server status
    """
    @staticmethod
    def __monitor_aggregates(monitor_openflow_aggregates=None):
        aggregates = Aggregate.objects.all()
        openflow_aggregate_leaf_name = "OpenFlowAggregate"
        if monitor_openflow_aggregates:
            aggregates = aggregates.filter(leaf_name=openflow_aggregate_leaf_name)
        else:
            aggregates = aggregates.exclude(leaf_name=openflow_aggregate_leaf_name)
        for aggregate in aggregates:
            #aggregate = aggregate.as_leaf_class()
            print "Now monitoring aggregate: %s" % aggregate.name
            AggregateMonitoringThread.monitor_aggregate_in_new_thread(aggregate)
        
        #Wait for threads
        for thread in threading.enumerate():
            if thread is not threading.currentThread():
                thread.join()
    
    @staticmethod
    def __monitor_sessions():
        SessionMonitoringThread.monitor_session_in_new_thread()
    
    @staticmethod
    def monitor():
        """
        Monitor aggregate status in two phases: OpenFlow and others
        Monitor sessions and delete old ones
        """
        aggregate_multiplier = 0
        session_multiplier = 0
        while True:
            # Monitor Aggregates
            print "---------------------------------"
            if aggregate_multiplier % AGGREGATE_OF_MULTIPLIER == 0:            
                aggregate_multiplier = 0
                print "Monitoring OpenFlow Aggregates"
                print ".............................."
                BackgroundMonitor.__monitor_aggregates("openflow")
            else:
                print "Monitoring other aggregates"
                print "..........................."
                BackgroundMonitor.__monitor_aggregates()
            aggregate_multiplier += 1
            print "---------------------------------"
            # Monitor sessions
            if session_multiplier % SESSION_MULTIPLIER == 0:
                session_multiplier = 0
                print "Monitoring Sessions"
                print "..................."
                BackgroundMonitor.__monitor_sessions()
            else:
                session_multiplier += 1
            print "---------------------------------"
            time.sleep(MONITORING_INTERVAL)	
