import threading
import time
import re
from openflow.optin_manager.sfa.openflow_utils.CreateOFSliver import CreateOFSliver
from openflow.optin_manager.sfa.openflow_utils.sliver_status import get_sliver_status
from openflow.optin_manager.sfa.openflow_utils.delete_slice import delete_slice
from openflow.optin_manager.sfa.openflow_utils.rspec3_to_expedient import get_fs_from_group 
from openflow.optin_manager.sfa.util.xrn import Xrn
from openflow.optin_manager.opts.models import Experiment, ExperimentFLowSpace
from openflow.optin_manager.xmlrpc_server.models import CallBackServerProxy, FVServerProxy
#TODO: Uncomment when merge
#from expedient.common.utils.mail import send_mail
from django.conf import settings 
from openflow.optin_manager.sfa.openflow_utils.ServiceThread import ServiceThread
from openflow.optin_manager.sfa.models import ExpiringComponents

#XXX TEST
from openflow.optin_manager.sfa.tests.data_example import test_switches, test_links

class OFShell:

        def __init__(self):
                pass
	
	@staticmethod
	def get_switches(used_switches=[]):
		complete_list = []
                switches = OFShell().get_raw_switches()
    		for switch in switches:
                        if len(used_switches)>0:
                             	if not switch[0] in used_switches:
                                    continue
                        if int(switch[1]['nPorts']) == 0:
                            #TODO: Uncomment when merge with ofelia.development
                            #send_mail('SFA OptinManager Error', 'There are some errors related with switches: GetSwitches() returned 0 ports.',settings.ROOT_EMAIL, [settings.ROOT_EMAIL])
                            raise Exception("The switch with dpid:%s has a connection problem and the OCF Island Manager has already been informed. Please try again later." % str(switch[0]))
                            #TODO: Send Mail to the Island Manager Here.
			port_list = switch[1]['portNames'].split(',')
			ports = list()
			for port in port_list:
				match = re.match(r'[\s]*(.*)\((.*)\)', port)
				ports.append({'port_name':match.group(1), 'port_num':match.group(2)})
                        complete_list.append({'dpid':switch[0], 'ports':ports})
		return complete_list

	@staticmethod
	def get_links():
                links = OFShell().get_raw_links()
		link_list = list()
		for link in links:
			link_list.append({ 'src':{ 'dpid':link[0],'port':link[1]}, 'dst':{'dpid':link[2], 'port':link[3]}})

		return link_list

	def GetNodes(self,slice_urn=None,authority=None):
                if not slice_urn:
		    switch_list = self.get_switches()
		    link_list = self.get_links()
		    return {'switches':switch_list, 'links':link_list}
                else:
                    nodes = list()
                    experiments = Experiment.objects.filter(slice_id=slice_urn)
                    for experiment in experiments:
                        expfss = ExperimentFLowSpace.objects.filter(exp = experiment.id)
                        for expfs in expfss:
                            if not expfs.dpid in nodes:
                                nodes.append(expfs.dpid)
                    switches = self.get_switches(flow_visor, nodes)
                    return {'switches':switches, 'links':[]}

	#def GetSlice(self,slicename,authority):
        #
	#	name = slicename 
	#	nodes = self.GetNodes()
	#	slices = dict()
	#	List = list()
	#	return slices	

	def StartSlice(self, slice_urn):
                #Look if the slice exists and return True or RecordNotFound
		experiments = Experiment.objects.filter(slice_id=str(slice_urn))
                if len(experiments) > 0:
                    return True
                else:
                    raise ""

	def StopSlice(self, slice_urn):
                #Look if the slice exists and return True or RecordNotFound
                experiments = Experiment.objects.filter(slice_id=slice_urn)
                if len(experiments) > 0:
                    return True
                else:
                    raise ""
	
	def RebootSlice(self, slice_urn):
                return self.StartSlice(slice_urn)
	

	def DeleteSlice(self, slice_urn):
                try:
                    delete_slice(slice_urn)
                    return 1  
                except:
                    raise ""

	def CreateSliver(self, requested_attributes, slice_urn, authority,expiration):
                project_description = 'SFA Project from %s' %authority
                slice_id = slice_urn
                for rspec_attrs in requested_attributes:
                    switch_slivers = get_fs_from_group(rspec_attrs['match'], rspec_attrs['group'])
                    controller = rspec_attrs['controller'][0]['url']
                    email = rspec_attrs['email']
                    email_pass = ''
                    if not self.check_req_switches(switch_slivers):
                        raise Exception("The Requested OF Switches on the RSpec do not match with the available OF switches of this island. Please check the datapath IDs of your Request RSpec.")
                    CreateOFSliver(slice_id, authority, project_description ,slice_urn, 'slice_description',controller, email, email_pass, switch_slivers)
                    if expiration:
                        #Since there is a synchronous connection, expiring_components table is easier to fill than VTAM
                        ExpiringComponents.objects.create(slice=slice_urn, authority=authority, expires=expiration)
		return 1

        def SliverStatus(self, slice_urn):
            sliver_status = get_sliver_status(slice_urn)
            if len(sliver_status) == 0:
                xrn = Xrn(slice_urn, 'slice')
                slice_leaf = xrn.get_leaf()
                sliver_status = ['The requested flowspace for slice %s is still pending for approval' %slice_leaf]
            granted_fs = {'granted_flowspaces':get_sliver_status(slice_urn)}
            return granted_fs

        def check_req_switches(self, switch_slivers):
            available_switches = self.get_raw_switches()
            for sliver in switch_slivers: 
                found = False
                for switch in available_switches:
                    if str(sliver['datapath_id']) == str(switch[0]): #Avoiding Unicodes
                        found = True
                        break
                if found == False:
                    return False
            return True

        def get_raw_switches(self):
             try: 
                 #raise ""
                 fv =  FVServerProxy.objects.all()[0]
                 switches = fv.get_switches()
             except Exception as e:
                 switches = test_switches
                 #raise e
             return switches

        def get_raw_links(self):
             try:
                 #raise ""
                 fv = FVServerProxy.objects.all()[0]  
                 links = fv.get_links()
             except Exception as e:
                 links = test_links
                 #raise e
             return links
