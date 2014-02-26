from plugins.vt_plugin.controller.dispatchers.MonitoringResponseDispatcher import MonitoringResponseDispatcher
from plugins.vt_plugin.models.VTServer import VTServer
from plugins.vt_plugin.models.VM import VM
import xmlrpclib

class InformationDispatcher:

    @staticmethod
    def force_update_vms(client_id='None', vm_id='None'):
        if client_id != 'None':
            server = VTServer.objects.get(id=client_id)
            client_id = server.getUUID()
        else:
            vm = VM.objects.get(id=vm_id)
            server = VTServer.objects.get(uuid=vm.serverID)
            vm_id = vm.getUUID() 
        client = server.aggregate.as_leaf_class().client
        vt_am = xmlrpclib.ServerProxy('https://'+client.username+':'+client.password+'@'+client.url[8:])
        raw_updates = vt_am.force_update_exp_vms(client_id, vm_id)
        updated_vms = InformationDispatcher.__process_updated_vms(raw_updates)
        print "Updated VMs--------->", updated_vms

    @staticmethod
    def __process_updated_vms(updated_vms):
        simple_actions = dict()
        for vm in VM.objects.all():
            if vm.getUUID() in updated_vms.keys():
                vm.setState("running")
                vm.save()
                simple_actions[vm.getUUID()] = "running"
            else:
                if vm.getState() in ['deleting...', 'failed', 'on queue', 'unknown']:
                    vm.delete()
                    simple_actions[vm.getUUID()] = "deleted"
                elif vm.getState() in ['running', "starting...", "stopping..."] :
                    vm.setState('stopped')
                    vm.save()
                    simple_actions[vm.getUUID()] = "stopped"
                else:
                    continue
        #TODO eval use of simple actions
        return updated_vms


