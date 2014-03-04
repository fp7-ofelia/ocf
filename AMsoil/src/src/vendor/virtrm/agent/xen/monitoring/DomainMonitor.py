import libvirt

from xen.XendManager import XendManager
from utils.Logger import Logger
	
con =  libvirt.openReadOnly(None)

class DomainMonitor:

	logger = Logger.getLogger()

	@staticmethod
	def retriveActiveDomainsByUUID(con):

		domainIds = con.listDomainsID()
		doms = list()

		for dId in domainIds:

			#Skip domain0
			if dId == 0:
				continue
	
			domain = con.lookupByID(dId)
			doms.append(domain.UUIDString())
			#DomainMonitor.logger.debug("Appending: "str(domain.UUIDString()))

		return doms 



