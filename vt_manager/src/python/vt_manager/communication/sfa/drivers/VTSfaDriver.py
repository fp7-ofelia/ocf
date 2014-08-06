import time

import datetime

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

# SSH keys for easy user access
from vt_manager.models.VirtualMachineKeys import VirtualMachineKeys

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
					logging.info("LDAP: deleting project in LDAP of SSH gateway")
					session = ldapManager()
					con = session.bind()
					if con:
						ldapprj = "%s.%s" % (authority, slicename)
						ldapprj = ldapprj.replace("\\" ,"")
						#logging.error("ldapprj: "+ ldapprj)
						status = session.delProject(con,ldapprj)
						if not status:
							logging.error("Cannot delete entry in LDAP of the SSH gateway")
					else:
						logging.error("Cannot contact LDAP of the SSH gateway")
				except:
					logging.error("Cannot contact LDAP of the SSH gateway")
			elif action == 'reset_slice':
				self.shell.RebootSlice(vm['node-id'],vm['vm-id'])
		return 1

        def create_sliver (self,slice_leaf,authority,rspec_string, users, options, expiration_date):
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
                                try:
                                       for user in users:
                                           xrn = Xrn(user['urn'], 'user')
                                           user_name = xrn.get_leaf()
                                           # Store user SSH key for future use
                                           for user_key in user['keys']:
                                               if not VirtualMachineKeys.objects.filter(project_uuid=vm["project-id"], slice_uuid=vm["slice-id"], vm_uuid=vm['uuid'],user_name=user_name ,ssh_key=user_key):
                                                   key_entry = VirtualMachineKeys(project_uuid=vm["project-id"], slice_uuid=vm["slice-id"], vm_uuid=vm['uuid'],user_name=user_name ,ssh_key=user_key)
                                                   key_entry.save()
                                except Exception as e:
                                           logging.error("create_sliver > Could not store user SSH key. Details: %s" % str(e))     
				#ip = self.shell.get_ip_from_vm(vm_name=vm['name'],slice_name=vm['slice-name'],project=authority)
				#created_vms.append({'vm-name':vm['name'],'vm-ip':ip,'vm-state':'ongoing','slice-name':slice_leaf,'node-name':node.name})
		#add ssh keys to ldap of ssh gateway
		if len(nodes):
			logging.info("create_slice > Connecting to LDAP")
			session = ldapManager()
			con = session.bind()
			logging.info("create_slice > Connected to LDAP. Connection: %s" % str(con))
			if con:
				logging.warning("LDAP: trying to create the following users: %s" % str(users))
				for user in users:
					logging.warning("Sending users to LDAP")
					#logging.error("project: "+str(projectName)+" slicename"+str(sliceName))
					ldapprj = "%s.%s" % (projectName, sliceName)
					ldapprj = ldapprj.replace("\\" ,"")
					logging.warning("LDAP project: " + ldapprj)
					session.addModifyProjectUsers(con,user['urn'],ldapprj,user['keys'])
					logging.warning("User added to project: " + str(ldapprj) + ", SSH key: " + str(user['keys']))
				#status=session.addProject(con,projectName+"."+sliceName)
				#if status != 0:
					#logging.error("users"+users)
				#	for index,user in enumerate(users):
						#logging.error(user)
				#		status=session.addUser(con,"user"+str(index),user['urn'],projectName+"."+sliceName,user['keys'])
				#		if status ==0:
				#			logging.error("can't add user to ldap of ssh gateway:"+ str(user))
				#else:
				#	logging.error("can't add project to ldap of ssh gateway: "+projectName+"."+sliceName)
			else:
				logging.error("Cannot contact LDAP of the SSH gateway")

		#add ssh keys to ldap of ssh gateway
#		if len(nodes)!=0:
#			session=ldapManager()
 #       		con=session.bind()
#			if con !=0:
#				status=session.addProject(con,projectName+"."+sliceName)
#				if status != 0:
#					#logging.error("users"+users)
#					for index,user in enumerate(users):
#						#logging.error(user)
#						status=session.addUser(con,"user"+str(index),user['urn'],projectName+"."+sliceName,user['keys'])
#						if status ==0:
#							logging.error("can't add user to ldap of ssh gateway:"+ str(user))
#				else:
#					logging.error("can't add project to ldap of ssh gateway: "+projectName+"."+sliceName)
#			else:
#				logging.error("can't contact ldap of ssh gateway")

		
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
