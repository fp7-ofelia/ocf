import time

import datetime
#
from vt_manager.communication.sfa.util.faults import MissingSfaInfo, UnknownSfaType, \
    RecordNotFound, SfaNotImplemented, SliverDoesNotExist

from vt_manager.communication.sfa.util.defaultdict import defaultdict
from vt_manager.communication.sfa.util.sfatime import utcparse, datetime_to_string, datetime_to_epoch
from vt_manager.communication.sfa.util.xrn import Xrn, hrn_to_urn, get_leaf
from vt_manager.communication.sfa.util.cache import Cache
from vt_manager.communication.sfa.trust.credential import Credential

from vt_manager.communication.sfa.rspecs.version_manager import VersionManager
from vt_manager.communication.sfa.rspecs.rspec import RSpec

from vt_manager.communication.sfa.drivers.VMAggregate import VMAggregate
from vt_manager.communication.sfa.drivers.VTShell import VTShell
from vt_manager.communication.sfa.vm_utils.ldapManager import ldapManager

import logging

class VTSfaDriver:

	def __init__ (self, config):
		self.aggregate = VMAggregate()
		self.shell = VTShell()


	def list_resources (self,options):

		version_manager = VersionManager()
        	rspec_version = 'OcfVt'#version_manager.get_version(options.get('geni_rspec_version'))
        	version_string = "rspec_%s" % (rspec_version)
                slice_leaf = None
                if options.get("slice"):
                	slice_leaf = options['slice']
	        rspec =  self.aggregate.get_rspec(version=rspec_version,options=options, slice_leaf=slice_leaf)
       		return rspec

	def crud_slice(self,slice_leaf,authority, action=None):

		slicename = slice_leaf 
                try:
                        slice = self.shell.GetSlice(slicename,authority)
                except Exception as e:
                        raise RecordNotFound(slice_leaf)

		for vm in slice['vms']:
			if action == 'start_slice':
				self.shell.StartSlice(vm['node-id'],vm['vm-id'])
			elif action == 'stop_slice':
				self.shell.StopSlice(vm['node-id'],vm['vm-id'])
			elif action == 'delete_slice':
				self.shell.DeleteSlice(vm['node-id'],vm['vm-id'])
				try:
                        		session=ldapManager()
                        		con=session.bind()
                        		if con !=0:
                                		status=session.delProject(con,authority+"."+slicename)
                                		if status==0:
                                        		logging.error("can't delete entry in ldap of ssh gateway")
                        		else:
                                		logging.error("can't contact ldap of ssh gateway")
                		except:
            				logging.error("can't contact ldap of ssh gateway")
			elif action == 'reset_slice':
				self.shell.RebootSlice(vm['node-id'],vm['vm-id'])
		return 1

        def create_sliver (self,slice_leaf,authority,rspec_string, users, options, expiration_date):
                print "---------------Creating sliver LOL"
                rspec = RSpec(rspec_string,'OcfVt')
                requested_attributes = rspec.version.get_slice_attributes()
                requested_attributes = self.shell.convert_to_uuid(requested_attributes) #Converts component_id URNs to UUIDs
		projectName = authority#users[0]['slice_record']['authority']
		sliceName = slice_leaf
		self.shell.CreateSliver(requested_attributes,projectName,sliceName,expiration_date)
		created_vms = list()
		nodes = list()
		for slivers in requested_attributes:
			node = self.shell.GetNodes(uuid=slivers['component_id'])
			for vm in slivers['slivers']:
				#node = self.shell.GetNodes(uuid=vm['server-id'])
				if not node in nodes:
					nodes.append(node)
                                #ip = self.shell.get_ip_from_vm(vm_name=vm['name'],slice_name=vm['slice-name'],project=authority)
				#created_vms.append({'vm-name':vm['name'],'vm-ip':ip,'vm-state':'ongoing','slice-name':slice_leaf,'node-name':node.name})
	        print "----------------VM Stuff done"	
		#add ssh keys to ldap of ssh gateway
		if len(nodes)!=0:
			session=ldapManager()
        		con=session.bind()
			if con !=0:
				status=session.addProject(con,projectName+"."+sliceName)
				if status != 0:
					#logging.error("users"+users)
					for index,user in enumerate(users):
						#logging.error(user)
						status=session.addUser(con,"user"+str(index),user['urn'],projectName+"."+sliceName,user['keys'])
						if status ==0:
							logging.error("can't add user to ldap of ssh gateway:"+ str(user))
				else:
					logging.error("can't add project to ldap of ssh gateway: "+projectName+"."+sliceName)
			else:
				logging.error("can't contact ldap of ssh gateway")

		
		return self.aggregate.get_rspec(slice_leaf=slice_leaf,projectName=projectName,version=rspec.version,created_vms=created_vms,new_nodes=nodes)
	
	def sliver_status(self,slice_leaf,authority,options):
                slice = self.shell.GetSlice(slice_leaf,authority)
                result = dict()
                List = list()
                for vm in slice['vms']:
                        List.append({'vm-name':vm['vm-name'],'vm-ip':vm['vm-ip'],'vm-state': vm['vm-state'], 'node-name': vm['node-name']})
                return List  
  			
        def get_expiration(self,creds,slice_hrn):
                for cred in creds:
                	credential = Credential(string=cred)
                    	if credential.get_gid_caller().get_hrn() == slice_hrn:
                        	return credential.get_expiration()
                return None 
