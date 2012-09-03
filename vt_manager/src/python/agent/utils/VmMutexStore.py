from threading import Thread, Lock
from utils.Logger import Logger

'''
	@author: msune

 	VM mutex store; class that encapsulates MUTEX operations for VMs	

'''

#static variables
localmutex = Lock()

##Vm dictionary
##Composed id with project,slice and vmname	
_vmLocks={}
	

class VmMutexStore():
	
	logger = Logger.getLogger()	

	@staticmethod
	def __getKey(vm):
		return vm.project_id+vm.slice_id+vm.name
	@staticmethod
	def lock(vm):
		key = VmMutexStore.__getKey(vm)
		#VmMutexStore.logger.debug("Trying to lock>>>"+key)

		#This localExclusion is to prevent problems if never resources (dictionary entry) are freed in unlock method
		localmutex.acquire()
		if not _vmLocks.has_key(key):
			#VmMutexStore.logger.debug("Creating entry in the dict>>>"+key)
			#create Mutex for the VM
			_vmLocks[key] = Lock()
		#release local mutex
		localmutex.release()
		#Acquire specific VM lock
		#VmMutexStore.logger.debug("trying to acquire lock>>>"+key)
		_vmLocks.get(key).acquire()
		#VmMutexStore.logger.debug("Lock acquired>>>")
		return

	@staticmethod
	def unlock(vm):
		localmutex.acquire()

		#release specific VM lock
		#TODO: release resources in dict?
		_vmLocks.get(VmMutexStore.__getKey(vm)).release()
		#VmMutexStore.logger.debug("Lock released>>>"+VmMutexStore.__getKey(vm))

		localmutex.release()
		return		

