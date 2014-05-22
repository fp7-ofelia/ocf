from controller.dispatchers.provisioning.query import ProvisioningDispatcher
from controller.dispatchers.launcher import DispatcherLauncher
from controller.actions.action import ActionController
from controller.drivers.virt import VTDriver
from datetime import datetime, timedelta
from models.common.action import Action
from models.common.container import Container
from models.resources.virtualmachine import VirtualMachine
from models.resources.allocatedvm import AllocatedVM
from models.resources.vtserver import VTServer
from models.resources.xenserver import XenServer
from models.resources.xenvm import XenVM
from templates.manager import TemplateManager
from utils.base import db
from utils.expirationmanager import ExpirationManager
from utils.servicethread import ServiceThread
from utils.vmmanager import VMManager
from utils.xmlhelper import XmlHelper
from utils.xrn import *
import amsoil.core.log
import amsoil.core.pluginmanager as pm
import copy
import time
import utils.exceptions as virt_exception
import uuid

# AMsoil logger
logging=amsoil.core.log.getLogger('VTResourceManager')

'''
@author: SergioVidiella, CarolinaFernandez
'''

class VTResourceManager(object):
    config = pm.getService("config")
    worker = pm.getService("worker")
    translator = pm.getService("virtutils").Translator
    
    EXPIRY_CHECK_INTERVAL = config.get("virtrm.EXPIRATION_VM_CHECK_INTERVAL") 
    
    ALLOCATION_STATE_ALLOCATED = "allocated"
    ALLOCATION_STATE_PROVISIONED = "provisioned"
    
    def __init__(self):
        super(VTResourceManager, self).__init__()
        # Register callback for regular updates
        self.worker.addAsReccurring("virtrm", "check_vms_expiration", None, self.EXPIRY_CHECK_INTERVAL)
        self.expiration_manager = ExpirationManager()
        self.template_manager = TemplateManager()
    
    # Server methods
    def get_servers(self, uuid=None):
        """
        Get server by uuid. 
        If no uuid provided, return all servers.
        """
        if uuid:
            servers = get_server(uuid)
        else:
            servers = []
            server_objs = self.get_server_objects()
            logging.debug("********************** SERVER OBTAINED => %s" % str(server_objs))
            for server_obj in server_objs:
                logging.debug("******************** MODEL TO DICT")
                server = self.translator.model2dict(server_obj)
                templates = self.template_manager.get_templates_from_server(server["uuid"])
                if templates:
                    server["disc_image_templates"] = templates
                servers.append(server)
        return servers

    def get_server_objects(self, uuid=None):
        """
        Get server by uuid. 
        If no uuid provided, return all servers.
        """
        if uuid:
            servers = self.get_server_object(uuid)
        else:
            servers = VTDriver.get_all_servers()
        return servers

    def get_server(self, uuid):
        """
        Get server with a given UUID as a dict.
        """
        server_obj = self.get_server_object(uuid)
        server = self.translator.model2dict(server_obj)
        templates = self.template_manager.get_templates_from_server(server["uuid"])
        if templates:
            server["disc_image_templates"] = templates
        return server   

    def get_server_object(self, uuid):
        """
        Get server with a given UUID.
        """
        server = VTDriver.get_server_by_uuid(uuid)
        return server
    
    def get_server_info(self, uuid):
        """
        Retrieve info for a server with a given UUID.
        """
        pass

    def get_provisioned_vms_in_server(self, server_uuid):
        """
        Obtains list of provisioned VMs for a server with a given UUID as a dict.
        """
        vms = []
        vm_objs = self.get_provisioned_vms_object_in_server(server_uuid)
        for vm_obj in vm_objs:
            vm = self.get_vm_info(vm_obj)
            vms.append(vm)
        return vms
 
    def get_provisioned_vms_object_in_server(self, server_uuid):
        """
        Obtains list of provisioned VMs for a server with a given UUID.
        """
        server = self.get_server_object(server_uuid)
        vms = VTDriver.get_vms_in_server(server)
        return vms
    
    def get_allocated_vms_in_server(self, server_uuid):
        """
        Obtains list of allocated VMs for a server with given UUID as a dict.
        """
        vms = []
        vm_objs = self.get_allocated_vms_object_in_server(server_uuid)
        for vm_obj in vm_objs:
            vm = self.get_vm_info(vm_obj)
            vms.append(vm)
        return vms
    
    def get_allocated_vms_object_in_server(self, server_uuid):
        """
        Obtains list of alloacted VMs for a server with given UUID.
        """
        server = self.get_server_object(server_uuid)
        vms = get_allocated_vms_in_server(server)
        return vms

    # VM methods
    def get_vm_uuid_by_vm_urn(self, vm_urn):
        pass

    def get_vm_urn_by_bm_uuid(self, vm_uuid):
        pass

    def get_vm_info(self, vm):
        logging.debug("*********** STARTING MODEL VM %s TO DICT..." % str(vm.uuid))
        # Generate a dictionary from the VM
        vm_dict = self.translator.model2dict(vm)
        logging.debug("*********** TRANSLATION COMPLETE...")
        logging.debug("*********** ADDING EXPIRATION INFORMATION...")
        # Add the Expiration information
        try:
            generation_time = self.expiration_manager.get_start_time_by_vm_uuid(vm_dict["uuid"])
        except:
            generation_time = None
        if generation_time:
            vm_dict['generation_time'] = generation_time
        try:
            expiration_time = self.expiration_manager.get_end_time_by_vm_uuid(vm_dict["uuid"])
        except:
            expiration_time = None
        if expiration_time:
            vm_dict['expiration_time'] = expiration_time
        logging.debug("*********** EXPIRATION INFORMATION ADDED...")
        logging.debug("*********** ADDING TEMPLATE INFORMATION TO VM %s..." % str(vm_dict['uuid']))
        # Add the Template information
        template = self.template_manager.get_template_from_vm(vm_dict["uuid"])
        vm_dict["disc_image"] = template
        logging.debug("*********** TEMPLATE INFORMATION ADDED...")
        # Obtain the server information
        # TODO: Automatize this
        logging.debug("*********** ADDING SERVER INFORMATION...")
        server = vm.server
        #XXX: Very ugly, fix this
        try:
            server = server[0]
        except:
            pass
        logging.debug("******************** SERVER IS => %s" % str(server))
        vm_dict["server_name"] = server.get_name()
        if not "server_uuid" in vm_dict.keys():
            vm_dict["server_uuid"] = server.get_uuid()
        logging.debug("*********** SERVER INFORMATION ADDED...")
        container_gid = self.get_vm_container(vm.get_urn())
        if container_gid:
            vm_dict["container_urn"] = container_gid
        return vm_dict
    
    def get_vm(self, vm_uuid):
        try:
            vm = self.get_vm_object(vm_uuid)
        except:
            raise virt_exception.VirtVMNotFound(vm_uuid)
        vm_dict = self.get_vm_info(vm)
        return vm_dict
         

    def get_vm_object(self, vm_uuid):
        try:
            vm = VTDriver.get_vm_by_uuid(vm_uuid)
        except:
            try:
                vm = VTDriver.get_vm_allocated_by_uuid(vm_uuid)
            except:
                raise virt_exception.VirtVMNotFound(vm_uuid)
        return vm

    def get_vm_by_urn(self, vm_urn):
        try:
            vm = self.get_vm_object_by_urn(vm_urn)
            vm_info = self.get_vm_info(vm)
        except:
             raise virt_exception.VirtVMNotFound(vm_urn)
        return vm_info

    def get_vm_object_by_urn(self, vm_urn):
        try:
            vm = VirtualMachine.query.filter_by(urn=vm_urn).one()
        except:
            raise type .VirtVMNotFound(vm_urn)
        return vm
 
    def get_vm_allocated_by_urn(self, vm_urn):
        try:
            vm = self.get_vm_allocated_object_by_urn
            vm_info = self.get_vm_info(vm)
        except:
            raise virt_exception.VirtVMNotFound(vm_urn)
        return vm_info

    def get_vm_allocated_object_by_urn(self, vm_urn):
        try:
            vm = self.get_vm_object_by_urn(vm_urn)
            if vm.get_state() != VirtualMachine.ALLOCATED_STATE:
                raise virt_exception.VirtVMNotFound(vm_urn)
        except Exception as e:
            raise e
        return vm

    def get_vms_in_container(self, container_gid, prefix=""):
        vms_info = list()
        try:
            logging.debug("*********************** STARTING QUERY")
            vms = self.get_vm_objects_in_container(container_gid, prefix)
            logging.debug("*********************** ENDING QUERY")
        except Exception as e:
            raise e
        for vm in vms:
            vm_info = self.get_vm_info(vm)
            vms_info.append(vm_info)
        return vms_info

    def get_vm_objects_in_container(self, container_gid, prefix=""):
        """
        Get all VMs in container with given container_gid and prefix
        """
        logging.debug("*************** CONTAINER GID => %s" % container_gid)
        logging.debug("*************** CONTAINER PREFIX => %s" % prefix)
        try:
            container = Container.query.filter_by(GID=container_gid, prefix=prefix).one()
            logging.debug("******************* Model.query => %s" % (str(type(Container.query))))
            logging.debug("******************* db.session.query(Model) => %s" % str(type(db.session.query(Container))))
            logging.debug("***************** CONTAINER OBTAINED %s => %s" % (container_gid, str(container)))
        except:
            raise virt_exception.VirtContainerNotFound(container_gid)
        logging.debug("****************** CONTAINER VMs => %s" % str(container.vms))
        vms = container.vms
        logging.debug("***************** VMs OBTAINED => %s" % str(vms))
#        if not vms:
#            logging.debug("**************** OPS, NO VMS ********************")
#            raise virt_exception.VirtNoResourcesInContainer(str(container_gid))
        # XXX: Ugly because of SQLAlchemy limitations. 
        # Association proxy is attached with the parent class.
        # Obtain the objects directly from the DB at this point.
        vms_in_container = list()
        for vm in vms:
            vm_in_container = VirtualMachine.query.filter_by(uuid=vm.get_uuid()).one()
            vms_in_container.append(vm_in_container)
        return vms_in_container

    def get_provisioned_vms_in_containter(self, container_gid, prefix=""):
        provisioned_vms = list()
        try:
            vms = self.get_provisioned_vm_objects_in_container(container_gid, prefix)
        except Exception as e:
            raise e
        for vm in vms:
            provisioned_vm = self.get_vm_info(vm)
            provisioned_vms.append(provisioned_vm)
        return provisioned_vms
    
    def get_provisioned_vm_objects_in_container(self, container_gid, prefix=""):
        """
        Get all VMs provisioned (created) in a given container.
        """
        provisioned_vms = list()
        try:
            vms = self.get_vm_objects_in_container(container_gid, prefix)
        except Exception as e:
            raise e
        # Filter by the VM state
        # Done this way for a better Exception threatment
        for vm in vms:
            if vm.get_state() != VirtualMachine.ALLOCATED_STATE:
                provisioned_vms.append(vm)
        if not provisioned_vms:
            raise virt_exception.VirtNoResourcesInContainer(container_gid)
        return provisioned_vms

    def get_allocated_vms_in_container(self, container_gid, prefix=""):
        allocated_vms = list()
        logging.debug("*************** CONTAINER GID => %s" % container_gid)
        logging.debug("*************** CONTAINER PREFIX => %s" % prefix)
        try:
            vms = self.get_allocated_vm_objects_in_container(container_gid, prefix)
            logging.debug("*********** VMs IN CONTAINER => %s" % (str(vms)))
        except Exception as e:
            raise e
        logging.debug("************** OBTAIN THE VMs INFORMATION...")
        for vm in vms:
            allocated_vm = self.get_vm_info(vm)
            allocated_vms.append(allocated_vm)
        return allocated_vms

    def get_allocated_vm_objects_in_container(self, container_gid, prefix=""):
        """
        Get all VMs allocated (reserved) in a given container.
        """
        allocated_vms = list()
        logging.debug("*************** CONTAINER GID => %s" % container_gid)
        logging.debug("*************** CONTAINER PREFIX => %s" % prefix)
        try:
            vms = self.get_vm_objects_in_container(container_gid, prefix)
            logging.debug("*************** VMs RECEIVED => %s" % str(vms))
        except Exception as e:
            logging.debug("**************** OPS, ERROR HERE *************")
            raise e
        # Filter by the VM state
        # Done this way for a better Exception threatment
        for vm in vms:
            if vm.get_state() == VirtualMachine.ALLOCATED_STATE:
                allocated_vms.append(vm)
        if not allocated_vms:
            raise virt_exception.VirtNoResourcesInContainer(container_gid)
        return allocated_vms
    
    def _destroy_vm(self, vm_id, server_uuid):
        if not server_uuid:
            server_uuid = XenDriver.get_server_uuid_by_vm_id(vm_id)
        try:
            VTDriver.propagate_action_to_provisioning_dispatcher(vm_id, server_uuid, Action.PROVISIONING_VM_DELETE_TYPE)
            return "success"
        except Exception as e:
            return "error" 

    def provision_vm(self, vm_dict, end_time):
        """
        Provision (create) previously allocated (reserved) VM.
        """
        # First make sure that the requested end_time is a valid expiration time
        logging.debug("********** STARTING PROVISIONING...")
        try:
            self.expiration_manager.check_valid_reservation_time(end_time)
        except:
            raise virt_exception.VirtMaxVMDurationExceeded(end_time)
        logging.debug("********** EXPIRATION OK...")
        # Get the Container of the VM
        container = Container.query.filter(Container.vms.any(uuid=vm_dict['uuid'])).one()
        container_gid = container.get_GID()
        container_prefix = container.get_prefix()
        logging.debug("********** CONTAINER %s OK..." % container_gid)
        # Obtain the associated template
        template = self.template_manager.get_template_from_vm(vm_dict['uuid'])
        logging.debug("********** TEMPLATE OK...")
        # Make {vm_dict} a valid dictionary for the XML class
        # XXX: Some information is still hardcoded by now
        server = self.get_server_object(vm_dict['server_uuid'])
        logging.debug("********** SERVER %s WITH UUID %s OK..." %(vm_dict['server_name'], vm_dict['server_uuid']))
        logging.debug("********** CREATING DICTIONARY...")
        # The dictionary must be easy to work with
        vm_uuid = vm_dict.pop('uuid')
        dictionary = dict()
        # Add the Server information
        dictionary['server'] = dict()
        dictionary['server']['uuid'] = vm_dict.pop('server_uuid')
        dictionary['server']['virtualization_type'] = server.get_virtualization_technology()
        # Add the VM information
        vm_dict['status'] = VirtualMachine.ONQUEUE_STATE
        vm_dict['uuid'] = uuid.uuid4()
	vm_dict['virtualization_type'] = server.get_virtualization_technology()
	vm_dict['server_id'] = dictionary['server']['uuid']
        dictionary['xen_configuration'] = vm_dict.pop('disc_image')
        dictionary['xen_configuration']['memory_mb'] = vm_dict.pop('memory_mb')
        dictionary['xen_configuration']['hd_origin_path'] = 'default/default.tar.gz'
        dictionary['vm'] = vm_dict
        logging.debug("********** DICTIONARY CREATED...")
        # Deallocate the current VM
        logging.debug("********** DEALLOCATING VM %s WITH UUID %s" % (vm_dict['name'], vm_dict['uuid']))
        try:
            logging.debug("********** DEALLOCATING...")
            self.delete_vm_by_uuid(vm_uuid)
            logging.debug("********** DEALLOCATED...")
        except Exception as e:
            logging.debug("********** DEALLOCATION FAILED ***********")
            raise e
        # Once deallocated, start the vm creation
        try: 
            logging.debug("********** PROVISIONING...")
            provisioned_vm = self.create_vm(dictionary, template, container_gid, container_prefix, end_time) 
            logging.debug("********** PROVISIONED...")
        except Exception as e:
            raise e
        return provisioned_vm

    def get_container_for_given_vm(self, vm_name, container_gid, prefix=""):
        """
        Obtain a Container object with the given GID and prefix.
        For the given container, check that any VM exists with the given name.
        If no container is returned create a new one.
        """
        container = Container.query.filter_by(GID=container_gid, prefix=prefix).all()
        logging.debug("*********** CONTAINERS => %s" % str(container))
        if len(container) == 1:
            logging.debug("********** SOLO 1")
            container = container[0]
            # If the Container exists, check if the VM name is already taken
            for vm in container.vms:
                if vm.name == vm_name:
                    # If any contained VM has the desired name, raise an error
                    raise virt_exception.VirtVmNameAlreadyTaken(vm_name)
        elif len(container) == 0:
            container = Container(container_gid, prefix, None, True)
        else:
            raise virt_exception.VirtContainerDuplicated(container_gid)
        return container

    def get_vm_container(self, vm_urn):
        result_container = None
        containers = Container.query.all()
        for container in containers:
            for vm in container.vms:
                if vm.urn == vm_urn:
                    result_container = container.get_GID()
                    break
        return result_container 

    def create_vm(self, args_dict, template, container_gid, prefix="", end_time=None):
        """
        Create a new VM with the given information related to a Container.
        """
        # First make sure that the requested end_time is a valid expiration time
        try:
            self.expiration_manager.check_valid_reservation_time(end_time)
        except:
            raise virt_exception.VirtMaxVMDurationExceeded(end_time)
        # Make sure any VM with the given name exists in the Container with the given GID and prefix.
        try:
            container = self.get_container_for_given_vm(args_dict["vm"]["name"], container_gid, prefix)
        except Exception as e:
            raise e
        # Obtain the provisioning RSpec from the dictionary
        provisioning_rspec = self.get_provisioning_rspec_from_dict(copy.deepcopy(args_dict))
        # Once we have the provisioning Rspec, call the Provisioning Dispatcher
        try:
            logging.debug("*************** CALL AGENT...")
            ProvisioningDispatcher.process(provisioning_rspec.query.provisioning, 'SFA.OCF.VTM')
        except Exception as e:
            # If the provisioning fails at any point, try tho destroy the created VM
            db.session.rollback()
            try:
                self.delete_vm_by_uuid(vm_class.uuid)
            except:
                pass
            logging.debug("*************** AGENT FAILED...")
            raise virt_exception.VirtVMCreationError(args_dict['vm']['name'])
        # Make sure that the VM has been created
        vm_class = provisioning_rspec.query.provisioning.action[0].server.virtual_machines[0]
        try:
            vm = self.get_vm_object(vm_class.uuid)
            logging.debug("************************ VM UUID => %s" % str(vm.uuid))
        except Exception as e:
            db.session.rollback()
            raise VirtVMCreationError(vm_class.uuid)
        # Attach the Expiration time to the VM
        try:
            self.expiration_manager.add_expiration_to_vm_by_uuid(vm.get_uuid(), end_time)
        except Exception as e:
            raise e
        # Attach the VM to a Container
        container.vms.append(vm)
        container.save()
        # Attach the Template Information to the VM
        try:
            self.template_manager.add_template_to_vm(vm.get_uuid(), template)
        except Exception as e:
            raise e
        # Add the URN
        logging.debug("******************* ALL OK AT THIS POINT")
        logging.debug("******************* VM DICT => %s" % str(args_dict))
        logging.debug("******************* URN IN DICT => %s" % str(args_dict['vm']['urn']))
        vm.set_urn(args_dict['vm']['urn'])
        # Once created, obtain the VM info
        created_vm = self.get_vm_info(vm)
        return created_vm

    def extend_vm_expiration_by_uuid(self, vm_uuid, expiration_time):
        try:
            self.expiration_manager.update_expiration_by_vm_uuid(vm_uuid, expiration_time)
        except Exception as e:
            raise e
        vm = self.get_vm(vm_uuid)
        return vm

    # XXX: This code should not be here
    def get_provisioning_rspec_from_dict(self, args_dict):
        logging.debug("*************** OBTAINING RSPEC...")
        provisioning_rspec = XmlHelper.get_simple_action_query()
        # Fill the action parameters
        logging.debug("*************** OBTAIN ACTION...")
        action_class = provisioning_rspec.query.provisioning.action[0]
        logging.debug("*************** FILL PARAMS...")
        action_class.type_ = "create"
        action_class.id = uuid.uuid4()
        # Fill the server parameters
        logging.debug("*************** OBTAIN SERVER...")
        server_dict = args_dict.pop("server")
        logging.debug("*************** FILL PARAMS...")
        server_class = action_class.server
        self.translator.dict2xml(server_dict, server_class)
        # Fill the VirtualMachine parameters
        logging.debug("*************** OBTAIN VM...")
        vm_dict = args_dict.pop("vm")
        logging.debug("*************** FILL PARAMS...")
        logging.debug("************* OPERATING SYSTEM TYPE IS %s" % vm_dict['operating_system_type'])
        vm_class = server_class.virtual_machines[0]
        self.translator.dict2xml(vm_dict, vm_class)
        logging.debug("************* OPERATING SYSTEM TYPE NOW IS %s" % vm_class.operating_system_type)
        # Fill the XenConfiguration parameters
        logging.debug("*************** OBTAIN XEN CONFIGURATOR...")
        xen_dict = args_dict.pop('xen_configuration')
        xen_class = vm_class.xen_configuration
        logging.debug("*************** FILL PARAMS...")
        self.translator.dict2xml(xen_dict, xen_class)
        # Fill the Interfaces parameteres
        # XXX: Currently this information is empty
        logging.debug("*************** OBTAIN INTERFACES...")
        interface_class = xen_class.interfaces.interface[0]
        logging.debug("*************** FILL PARAMS...")
        interface_class.ismgmt = "False"
        return provisioning_rspec

#    def _provision_vms(self, vm_params, slice_urn, project_name):
#        """
#        Provision (create) VMs.
#        """
#        created_vms = list()
#        slice_hrn, urn_type = urn_to_hrn(slice_urn)
#        slice_name = get_leaf(slice_hrn)
#        provisioning_rspecs, actions = VMManager.get_action_instance(vm_params,project_name,slice_name)
#        vm_results = dict()
#        for provisioning_rspec, action in zip(provisioning_rspecs, actions):
#            ServiceThread.start_method_in_new_thread(ProvisioningDispatcher.process, provisioning_rspec, 'SFA.OCF.VTM')
#            vm = provisioning_rspec.action[0].server.virtual_machines[0]
#            vm_hrn = 'geni.gpo.gcf.' + vm.slice_name + '.' + vm.name
#            vm_urn = hrn_to_urn(vm_hrn, 'sliver')
#            server = VTDriver.get_server_by_uuid(vm.server_id)
#            if server.name not in vm_results.keys():
#                vm_results[server.name] = list()
#            vm_results[server.name].append({'name':vm_urn, 'status':'ongoing'})
#        return vm_results
    
    # VM status methods
    def crud_vm_by_urn(self, vm_urn):
        try:
            vm = self.get_vm_object_by_urn(vm_urn)
            result_vm = self.crud_vm(vm)
        except Exception as e:
            raise e
        return result_vm

    def crud_vm(self, vm, action):
        try:
            vm_id = vm.get_id()
            server_uuid = vm.get_server().get_uuid()
        except Exception as e:
            raise virt_exception.VirtDatabaseError()
        try:
            if action == "start":
                self.start_vm()
            elif action == "stop":
                self.stop_vm()
            elif action == "restart":
                self.restart_vm()
            else:
                raise virt_exception.VirtUnsupportedAction(action)
        except Exception as e:
            raise e
        result_vm = get_vm_info(vm)
        return result_vm

    def start_vm(self, vm_id, server_uuid):
        try:
            VTDriver.propagate_action_to_provisioning_dispatcher(vm_id, server_uuid, Action.PROVISIONING_VM_START_TYPE)
        except Exception as e:
            raise virt_exception.VirtOperationalError(vm_id)
    
    def pause_vm(self, vm_id, server_uuid):
        """
        Stores VM status in memory.
        Xen: xm pause <my_vm>
        See http://stackoverflow.com/questions/11438922/how-does-xen-pause-a-vm
        """
        pass
    
    def stop_vm(self, vm_id, server_uuid):
        try:
            VTDriver.propagate_action_to_provisioning_dispatcher(vm_id, server_uuid, Action.PROVISIONING_VM_STOP_TYPE)
        except Exception as e:
            raise virt_exception.VirtOperationalError(vm_id)
    
    def restart_vm(self, vm_id, server_uuid):
        try:
            VTDriver.propagate_action_to_provisioning_dispatcher(vm_id, server_uuid, Action.PROVISIONING_VM_REBOOT_TYPE)
        except Exception as e:
            raise virt_exception.VirtOperationalError(vm_id)
    
    def delete_vm_by_uuid(self, vm_uuid):
        logging.debug("********** DELETING VM WITH UUID %s..." % vm_uuid)
        try:
            vm = VTDriver.get_vm_by_uuid(vm_uuid)
            logging.debug("********** VM OBTAINED")
            deleted_vm = self.delete_vm(vm)
            logging.debug("************* FINALLY DELETED => %s" % str(deleted_vm))
            return deleted_vm
        except Exception as e:
            logging.debug("****************** EXCEPTION => %s" % str(e))
            raise e

    def delete_vm(self, vm):
        expiration = self.expiration_manager.get_expiration_by_vm_uuid(vm.get_uuid())
        # template = self.template_manager.get_template_from_vm(vm.get_uuid())
        try:
            if vm.state == VirtualMachine.ALLOCATED_STATE:
                deleted_vm = self.deallocate_vm(vm)
            else:
                deleted_vm = self.destroy_vm(vm)
        except Exception as e:
            raise e
        # Once the VM has been deleted, delete the related Expiration
        self.expiration_manager.delete_expiration(expiration)
        logging.debug("************* EXPIRATION DELETED")
        #self.template_manager.remove_template_for_vm(template.id)
        # Change the VM status to deleted
        deleted_vm['state'] = 'deleted'
        return deleted_vm

    def destroy_vm(self, vm):
        deleted_vm = self.get_vm_info(vm)
        # Send the asynchronus signal to the Agent
        # Return a message indicating the deleting is being performed
        action_type = Action.PROVISIONING_VM_DELETE_TYPE,
        rspec = XmlHelper.get_simple_action_specific_query(action_type, vm.server[0].uuid)
        ActionController.populate_new_action_with_vm(rspec.query.provisioning.action[0], vm)
        ServiceThread.start_method_in_new_thread(DispatcherLauncher.process_query, rspec)
        return deleted_vm
 
#    def delete_vm(self, vm_urn, slice_name=None):
#        vm_hrn, hrn_type = urn_to_hrn(vm_urn)
#        if not slice_name:
#            slice_name = get_leaf(get_authority(vm_hrn))
#        vm_name = get_leaf(vm_hrn)
#        vm = db_session.query(VirtualMachine).filter(VirtualMachine.name == vm_name).filter(VirtualMachine.slice_name == slice_name).first()
#        if vm != None:
#             db_session.expunge(vm)
#             deleted_vm = self._destroy_vm_with_expiration(vm.id)
#        else:
#             vm = db_session.query(VMAllocated).filter(VMAllocated.name == vm_name).first()
#             if vm != None:
#                db_session.expunge(vm)
#                deleted_vm = self._unallocate_vm(vm.id)
#                if not deleted_vm:
#                    deleted_vm = dict()
#                    deleted_vm = dict()
#                    deleted_vm['name'] = vm_urn
#                    deleted_vm['expiration'] = None
#                    deleted_vm['error'] = "The requested VM does not exist, it may have expired"
#             else:
#                deleted_vm = dict()
#                deleted_vm['name'] = vm_urn
#                deleted_vm['expiration'] = None
#                deleted_vm['error'] = "The requested VM does not exist, it may have expired"
#        return deleted_vm
    
    # Slice methods
    def add_vm_to_slice(self, slice_urn, vm_urn):
        """
        Add VM to slive with given URN.
        """
        pass
    
    def remove_vm_to_slice(self, slice_urn, vm_urn):
        """
        Remove VM from slive with given URN.
        """
        pass
    
    def check_project_exists(self, project_name):
        '''
        Check if any VM exists with the given project name and return the related UUID.
        If the project is not asigned to any VM, generate a new UUID for it.
        '''
        vm_in_project = VirtualMachine.query.filter_by(project_name=project_name).first()
        # If exists, assign the same UUID
        if vm_in_project:
            project_uuid = vm_in_project.get_project_id()
        else:
            project_uuid = uuid.uuid4()
        return project_uuid

    def check_slice_exists_in_project(self, project_name, slice_name):
        '''
        Check if any VM exists in the given slice and project, and return the related slice UUID.
        If the slice is not in any project, generate a new UUID for it.
        '''
        vm_in_slice = VirtualMachine.query.filter_by(project_name=project_name, slice_name=slice_name).first()
        if vm_in_slice:
            slice_uuid = vm_in_slice.get_slice_id()
        else:
            slice_uuid = uuid.uuid4()
        return slice_uuid

    
    # Allocation methods
    def allocate_vm(self, vm, end_time, container_gid, prefix=""):
        """
        Allocate a VM in the given container.
        """
        # Check if the Container exists
        try:
            container = self.get_container_for_given_vm(vm["name"], container_gid, prefix)
        except Exception as e:
            raise e
        # Check if the server is one of the given servers
        try: 
            server = VTServer.query.filter_by(uuid=vm["server_uuid"]).one()
            logging.debug("*********** SERVER %s HAS ATTRIBUTES %s" % (server.name, str(server.__dict__)))
        except:
            raise virt_exception.VirtServerNotFound(vm["server_uuid"])
        # Check if the expiration time is a valid time
        try:
            self.expiration_manager.check_valid_reservation_time(end_time)
        except:
            raise virt_exception.VirtMaxVMDurationExceeded(end_time)
        # XXX: This should be into the TemplateManager?
        # Try to obtain the Template definition
        try:
            template_info = vm.pop("template_definition")
        # Otherwhise we assume the "default" Template
        except:
            template_info = dict()
            template_info["template_name"] = "Default"
        # Check if the Template is a valid one and return it
        try:
            template = self.template_manager.get_template_by(template_info.values()[0])
        except:
            raise virt_exception.VirtTemplateNotFound(vm['urn'])
        logging.debug("************ TEMPLATE => %s" % str(template))
        # Check if the project and slice already exist
        project_uuid = self.check_project_exists(vm["project_name"])
        vm["project_id"] = project_uuid
        slice_uuid = self.check_slice_exists_in_project(vm["project_name"], vm["slice_name"])
        vm["slice_id"] = slice_uuid
        #XXX: Hardcoded due to the database limitations
        # The AllocatedVM model needs some information of the Template, obtain it and add to the dictionary
        vm["operating_system_type"] = template["operating_system_type"]
        vm["operating_system_distribution"] = template["operating_system_distribution"]
        vm["operating_system_version"] = template["operating_system_version"]
        # Allocate the required NetworkInterfaces (Resource Allocation)
        vm_allocated_interfaces = server.create_enslaved_vm_interfaces()
        vm["network_interfaces"] = vm_allocated_interfaces
        logging.debug("************ NETWORK_INTERFACES IS %s" % (str(vm_allocated_interfaces)))
        # Generate an Unique IDentificator
        vm['uuid'] = uuid.uuid4()
        # Generate the AllocatedVM model
        try:
            vm_allocated_model = self.translator.dict2class(vm, AllocatedVM)
            # Save the data into de database
            vm_allocated_model.save()
            # TODO: Create a NetworkInterface and asign to the VM
            logging.debug("************ RELATED SERVER IS %s WITH ATTRIBUTES %s" %(vm_allocated_model.server.name, str(vm_allocated_model.server)))
        except:
            db.session.rollback()
            # Try to destroy the allocated VM
            try:
                self.deallocate_vm(vm_allocated_model)
            except:
                 db.session.rollback()
            # Rollback the session
            raise VirtVMAllocationError(vm['urn'])
        # Associate the new VM with the Container
        container.vms.append(vm_allocated_model)
        # Add the expiration time to the allocated VM
        try:
            self.expiration_manager.add_expiration_to_vm_by_uuid(vm_allocated_model.get_uuid(), end_time)
        except Exception as e:
            # Rollback the session
            db.session.rollback()
            # Destroy the related VM
            try:
                self.deallocate_vm(vm_allocated_model)
            except:
                db.session.rollback()
            raise virt_exception.VirtMaxVMDurationExceeded(end_time)
        # Add the template to the allocated VM
        self.template_manager.add_template_to_vm(vm_allocated_model.get_uuid(), template)
        # Obtain the Allocated VM information
        vm_allocated_dict = self.get_vm(vm_allocated_model.get_uuid())
        return vm_allocated_dict
        
    def deallocate_vm(self, vm):
        """
        Delete the entry in the table of allocated VMs.
        """
        deleted_vm = self.get_vm_info(vm)
        logging.debug("************ VM TO DELETE => %s" % str(deleted_vm))
        try:
            vm.destroy()
        except:
            db.session.rollback()
            raise virt_exception.VirtDeallocateVMError(vm.urn)
        logging.debug("************ VM DELETED => %s" % str(deleted_vm))
        return deleted_vm
    
    # Authority methods
    def get_vms_in_authority(self, authority_urn):
        """
        Get list of VMs in authority with given URN.
        """
        pass
    
    def get_allocated_vms_in_authority(self, authority_urn):
        """
        Get list of allocated (reserved) VMs in authority with given URN.
        """
        pass
    
    def get_provisioned_vms_in_authority(self, authority_urn):
        """
        Get list of provisioned (created) VMs in authority with given URN.
        """
        pass
    
    @worker.outsideprocess
    def check_vms_expiration(self, params):
        """
        Checks expiration for both allocated and provisioned VMs
        and deletes accordingly, either from DB or disk.
        """
        # Get the expired VMs
        expired_vms = self.expiration_manager.get_expired_vms()
        # Delete the expired VMs
        for expired_vm in expired_vms:
            vm_uuid = expired_vm.get_uuid()
            self.delete_vm_by_uuid(vm_uuid)
            self.expiration_manager.delete_expiration_by_vm_uuid(vm_uuid)
        # Check if any Container is empty and delete it
        containers = Container.query.all()
        for container in containers:
            if not container.vms:
                container.destroy()
        return
    
    # Backup & migration methods
    # XXX Do not implement right now
    def copy_vm_to_slice(self, slice_urn, vm_urn):
        pass
    
    def move_vm_to_slice(self, slice_urn, vm_urn):
        pass
    
    def copy_vm_to_server(self, server_urn, vm_urn):
        pass
    
    def move_vm_to_server(self, server_urn, vm_urn):
        pass
    
    def update_template_to_server(self, server_urn, template_path):
        pass
    
    def get_vm_snapshot(self, server_urn, template_name):
        pass

