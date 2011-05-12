import libvirt
from xen.XendManager import XendManager
	
con =  libvirt.openReadOnly(None)

class DomainMonitor:

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
			#print str(domain.UUIDString())

		return doms 


doms = DomainMonitor.retriveActiveDomains(con)

for dom in doms:
	print dom

