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
	print "MONITORING >>>> " + aggregate.name
        try:
            agg = aggregate.as_leaf_class()
            agg_xmlrpc_server = "https://" + agg.client.username + ":" + agg.client.password + "@" + agg.client.url[8:]
            try:
                agg_info = XmlRpcClient.callRPCMethod(agg_xmlrpc_server, "get_am_info", "")
                print "agg info: " + str(agg_info)
                # Save fields only for OF AMs
                if aggregate.leaf_name == "OpenFlowAggregate":
                    aggregate.openflowaggregate.vlan_auto_assignment = agg_info["vlan_auto_assignment"]
                    aggregate.openflowaggregate.flowspace_auto_approval = agg_info["flowspace_auto_approval"]
                    # Save specific OpenFlowAggregate object
                    aggregate.openflowaggregate.straightSave()
            except Exception as e:
#                print "Aggregate " + aggregate.name + " did not offer information about automatic VLAN and flowspace granting"
                # Older OF AM APIs shall not contain 'get_am_info' method. Try 'ping' in that case:
                XmlRpcClient.callRPCMethod(agg_xmlrpc_server, "ping", "hello")
            print "Aggregate " + aggregate.name + " is alive"
            
            # If any of the above worked, mark as available
            aggregate.available = True
            #aggregate.save(permittee_kw = user.first_name)
            aggregate.straightSave()
        except Exception as e:
            #If fails for some reason mark as unreachable
            print e
            aggregate.available = False
            #aggregate.save(permittee_kw = user.first_name)
            print "Aggregate " + aggregate.name + " is DEAD!"
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
