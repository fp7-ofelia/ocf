from vt_manager.communication.XmlRpcClient import XmlRpcClient
from vt_manager.communication.utils.XmlHelper import XmlHelper
from vt_manager.controller.actions.ActionController import ActionController
from vt_manager.models.Action import Action
from vt_manager.utils.UrlUtils import UrlUtils

from vt_manager.controller.drivers.VTDriver import VTDriver
import xmlrpclib, threading, logging, copy
from vt_manager.models.ServerStatistics import ServerStatistics

'''
	author:lbergesio
	Encapsulates Statistics monitoring methods	
'''

class StatisticsMonitor(): 
	
	@staticmethod
	def updateStatistics():
		#Recover controlled servers
		servers = VTDriver.getAllServers()	
		empty_query = XmlHelper.getStatisticsQuery()
		
		for server in servers:
			try:
				query = copy.deepcopy(empty_query)
	
				action = ActionController.createNewAction(Action.MONITORING_SERVER_STATISTICS_TYPE,Action.QUEUED_STATUS,server.getUUID(),"")
	
	
	        	        query.query.monitoring.action[0].id = action.getUUID()
				query.query.monitoring.action[0].server.virtualization_type = server.getid = server.getVirtTech()
				logging.debug("LEODEBUG QUERY:\n"+XmlHelper.craftXmlClass(query))
		                XmlRpcClient.callRPCMethod(server.getAgentURL(),"send",UrlUtils.getOwnCallbackURL(),0,server.agentPassword,XmlHelper.craftXmlClass(query))
			except Exception as e:
				print "Could not request server %s statistics" % server.name	
				print e

	@staticmethod
	def storeStatistics(server):
		print "LEODEBUG LLEGA EL SERVIDOR CON UUID :%s" %server.uuid
		serverobj = VTDriver.getServerByUUID(server.uuid)
		record = server.stats.all()
		if len(record) > 1:
			raise Exception("Server %s has multiple statistics records" % serverobj.name)
		elif len(record) == 0:
			record = ServerStatistics()
			record.server = serverobj
		else:
			record = record[0]

		__fillStatisticsFromRspec(record, serverobj)

	def __fillStatisticsFromRspec(record, server):
		record.user_cpu = server.status.user_cpu
		record.sys_cpu = server.status.sys_cpu
		record.idle_cpu = server.status.idle_cpu
		record.used_memory = server.status.used_memory
		record.free_memory = server.status.free_memory
		record.total_memory = server.status.total_memory
		record.buffers_memory = server.status.buffers_memory
		for part in server.status.hd_space.partition:
			#XXX:It is not considered if the statistics record had an alrady existing 
			#partition not present in the new rspec...
			pobj = record.partitions.filter(name=part.name)
			if len(pobj) == 0:
				pobj = StatisticsPartition()
			else:
				pobj = pobj[0]
			pobj.name = part.name
			pobj.size = part.size
			pobj.used = part.used
			pobj.available = part.available
			pobj.used_ratio = part.used_ratio
			pobj.server = server
			pobj.save()
		record.save()

		
		
			
