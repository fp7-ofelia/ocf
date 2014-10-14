from plugins.vt_plugin.controller.dispatchers.MonitoringResponseDispatcher import MonitoringResponseDispatcher
from plugins.vt_plugin.models.Action import Action
from plugins.vt_plugin.models.VTServer import VTServer
from plugins.vt_plugin.models.VM import VM
import xmlrpclib

class InformationDispatcher:

    @staticmethod
    def force_delete_vm(vm):
        # Completely delete VM
        server = VTServer.objects.get(uuid = vm.serverID)
        server.vms.remove(vm)
        # Delete the associated entry in the database
        Action.objects.all().filter(vm = vm).delete()
        vm.completeDelete()
        # Keep actions table up-to-date after each deletion
        #Action.objects.all().exclude(vm__in = VM.objects.all()).delete()
    
    @staticmethod
    def force_update_vms(client_id="None", vm_id="None"):
        """
        Forces the update of the status of the VMs.
        Retrieves the server from the passed arguments and invokes
        the corresponding method on its VT AM.
        
        If this method fails, it means there was no VM
        If the server ("client_id") is not passed, it is obtained from the VM
        
        @param    client_id     ID of the server
        @param    vm_id         ID of the VM
        @return   nothing
        """
        raw_updates = dict()
        vm = None
        if client_id != "None":
            server = VTServer.objects.get(id=client_id)
            client_id = server.getUUID()
        else:
            vm = VM.objects.get(id=vm_id)
            server = VTServer.objects.get(uuid=vm.serverID)
            vm_id = vm.getUUID() 
        client = server.aggregate.as_leaf_class().client
      
        vt_am = xmlrpclib.ServerProxy("https://"+client.username+":"+client.password+"@"+client.url[8:])
        # If the previous method fails, it means that the VM could not be found in
        # the VT AM. In that case synchronize the Expedient model by deleting it.
        try:
            raw_updates = vt_am.force_update_exp_vms(client_id, vm_id)
        except Exception as e:
            if vm:
                # Completely delete VM
                InformationDispatcher.force_delete_vm(vm)
        updated_vms = InformationDispatcher.__process_updated_vms(raw_updates)

    @staticmethod
    def __process_updated_vms(updated_vms):
        simple_actions = dict()
        all_vms = VM.objects.all()
        for vm in all_vms:
            if vm.getUUID() in updated_vms.keys():
                vm.setState("running")
                vm.save()
                simple_actions[vm.getUUID()] = "running"
            else:
                # XXX: avoiding "on queue" and "unknown" states to avoid bad management
                #if vm.getState() in ["deleting...", "failed", "on queue", "unknown", "undefined"]:
                if vm.getState() in ["deleting...", "failed"]:
                    # Completely delete VM
                    InformationDispatcher.force_delete_vm(vm)
                    simple_actions[vm.getUUID()] = "deleted"
                elif vm.getState() in ["running", "starting...", "stopping..."]:
                    vm.setState("stopped")
                    vm.save()
                    simple_actions[vm.getUUID()] = "stopped"
                else:
                    continue
        #TODO eval use of simple actions
        return updated_vms

    @staticmethod
    def get_ocf_am_version(client_id):
        try:
          server = VTServer.objects.get(id=client_id)
          client = server.aggregate.as_leaf_class().client
          vt_am = xmlrpclib.ServerProxy("https://"+client.username+":"+client.password+"@"+client.url[8:])
          sv = vt_am.get_ocf_version()
          i = 1
          result = 0
          for num in sv.split(".").reverse():
              result += i * num
              i *= 10
          return result
        except:
          return  None #Equal or Below 0.7 version

