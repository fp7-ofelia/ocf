from threading import Thread
from expedient.clearinghouse.aggregate.models import *
from expedient.clearinghouse.monitoring.XmlRpcClient import XmlRpcClient

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
        from django.contrib.auth.models import User
        from django.contrib.auth import authenticate
        from expedient.clearinghouse.settings import ROOT_USERNAME, ROOT_PASSWORD
        user = authenticate(username=ROOT_USERNAME, password=ROOT_PASSWORD)
        kw = user
        if user is not None:
            print "USER AUTHENTICATED"
        try:
            agg = aggregate.as_leaf_class()
            XmlRpcClient.callRPCMethod('https://'+agg.client.username+':'+agg.client.password+'@'+agg.client.url[8:],"ping", "hello")
            print "VOY A PONE' TRU"
            aggregate.available = True
            #aggregate.save(permittee_kw = user.first_name)
            agg.save()
        except Exception as e:
            #If fails for some reason mark as unreachable
            print e
            aggregate.available = False
            #aggregate.save(permittee_kw = user.first_name)
            agg.save()
		
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
