from threading import Thread, Lock

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
	@staticmethod
	def __getKey(vm):
		return vm.project_id+vm.slice_id+vm.name
	@staticmethod
	def lock(vm):
		key = VmMutexStore.__getKey(vm)
		#print "Trying to lock>>>"+key

		#This localExclusion is to prevent problems if never resources (dictionary entry) are freed in unlock method
		localmutex.acquire()
		if not _vmLocks.has_key(key):
			
			#print "Creating entry in the dict>>>"+key
			
			#create Mutex for the VM
			_vmLocks[key] = Lock()
		#release local mutex
		localmutex.release()
		#Acquire specific VM lock
		#print "trying to acquire lock>>>"+key
		_vmLocks.get(key).acquire()
		#print "Lock acquired>>>"+key
		return

	@staticmethod
	def unlock(vm):
		localmutex.acquire()

		#release specific VM lock
		#TODO: release resources in dict?
		_vmLocks.get(VmMutexStore.__getKey(vm)).release()
		#print "Lock released>>>"+VmMutexStore.__getKey(vm)

		localmutex.release()
		return		

