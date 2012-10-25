import os
import sys
from vt_plugin.models import VM

class MonitoringResponseDispatcher():

    '''
    Handles all the VT AM vm provisioning responses and all the actions that go 
    from the VT AM to the VT Plugin
    '''

    @staticmethod
    def processResponse(response):
        print "---------------------->MonitoringResponseDispatcher.processResponse\n"
        for action in response.action:
		if action.id == "callback":
			try:
                        	vm = VM.objects.get(uuid = action.server.virtual_machines[0].uuid)
                	except Exception as e:
                        	raise e

			state = action.server.virtual_machines[0].status
                	if state == 'Started':
                        	vm.setState('running')
                	elif state == 'Stopped':
                        	vm.setState('created (stopped)')
                	else:
                        	vm.setState('unknown')
			vm.save()
	return

