from threading import Thread
from modules.aggregate.models import *
from modules.monitoring.XmlRpcClient import XmlRpcClient

'''
author:msune
Agent monitoring thread
'''

class AggregateMonitoringThread(Thread):
	
    __method = None
    __param = None

    '''
    Make sure Agent is up and running
    and updates status
    '''


    def __updateAggregateStatus(self, aggregate):
	print "MONITORING >>>> "+aggregate.name
        try:
            agg = aggregate.as_leaf_class()
            XmlRpcClient.callRPCMethod('https://'+agg.client.username+':'+agg.client.password+'@'+agg.client.url[8:],"ping", "hello")
            print "Aggregate "+aggregate.name+" is alive"
            aggregate.available = True
            #aggregate.save(permittee_kw = user.first_name)
            aggregate.straightSave()
        except Exception as e:
            #If fails for some reason mark as unreachable
            print e
            aggregate.available = False
            #aggregate.save(permittee_kw = user.first_name)
            print "Aggregate "+aggregate.name+" is DEAD!"
            aggregate.straightSave()
		
    @staticmethod
    def monitorAggregateInNewThread(param):
        thread = AggregateMonitoringThread()	
        thread.startMethod(param)
        return thread

    def startMethod(self,param):
        self.__method = self.__updateAggregateStatus 
        self.__param = param
        self.start()

    def run(self):	
        self.__method(self.__param)			
