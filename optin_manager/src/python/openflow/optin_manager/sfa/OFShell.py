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

#XXX TEST
#from openflow.optin_manager.sfa.tests.data_example import test_switches, test_links

class OFShell:

        def __init__(self):
                pass
	
	@staticmethod
	def get_switches(flow_visor, used_switches=[]):
		complete_list = []
    		try:
        		switches = flow_visor.get_switches()
    		except Exception as e:
                        #XXX:Test-Only
			#switches = test_switches 
    		for switch in switches:
                        if len(used_switches)>0:
                             	if not switch[0] in used_switches:
                                    continue
                        if int(switch[1]['nPorts']) == 0:
                            raise Exception("The switch with dpid:%s has a connection problem and the OCF Island Manager has already been informed. Please try again later." % str(switch[0]))
                            #TODO: Send Mail to the Island Manager Here.
			port_list = switch[1]['portNames'].split(',')
			ports = list()
			for port in port_list:
				match = re.match(r'[\s]*(.*)\((.*)\)', port)
				ports.append({'port_name':match.group(1), 'port_num':match.group(2)})
                        complete_list.append({'dpid':switch[0], 'ports':ports})
		print complete_list
		return complete_list

	@staticmethod
	def get_links(flow_visor):
		complete_list = []
                try:
                        links = flow_visor.get_links()
		except Exception as e:
                        #XXX:Test-Only
			#links = test_links 
		link_list = list()
		for link in links:
			link_list.append({ 'src':{ 'dpid':link[0],'port':link[1]}, 'dst':{'dpid':link[2], 'port':link[3]}})

		return link_list

	def GetNodes(self,slice_urn=None,authority=None):
                flow_visor = FVServerProxy.objects.all()[0] #XXX: Test_Only
                if not slice_urn:
		    switch_list = self.get_switches(flow_visor)
		    link_list = self.get_links(flow_visor)
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

	def CreateSliver(self, requested_attributes, slice_urn, authority):
                project_description = 'SFA Project from %s' %authority
                slice_id = slice_urn
                for rspec_attrs in requested_attributes:
                    switch_slivers = get_fs_from_group(rspec_attrs['match'], rspec_attrs['group'])
                    controller = rspec_attrs['controller'][0]['url']
                    email = rspec_attrs['email']
                    email_pass = ''
                    CreateOFSliver(slice_id, authority, project_description ,slice_urn, 'slice_description',controller, email, email_pass, switch_slivers)
		return 1

        def SliverStatus(self, slice_urn):
            sliver_status = get_sliver_status(slice_urn)
            if len(sliver_status) == 0:
                xrn = Xrn(slice_urn, 'slice')
                slice_leaf = xrn.get_leaf()
                sliver_status = ['The requested flowspace for slice %s is still pending for approval' %slice_leaf]
            granted_fs = {'granted_flowspaces':get_sliver_status(slice_urn)}
            return granted_fs

       
