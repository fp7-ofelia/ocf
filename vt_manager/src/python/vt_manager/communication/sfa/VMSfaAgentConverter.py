from vt_manager.communication.utils.XmlHelper import XmlHelper


class VMSfaAgentConverter:

    '''Class to pass the VM parameters to an RSpec Instance for ProvisioningDisaptcher'''

    @staticmethod
    def getOcfActionInstance(vm_parameters, server_parameters):

	rspec = XmlHelper.getSimpleActionQuery()
	server = rspec.query.provisioning.action[0]._type = 'create'
	
	
	
	
