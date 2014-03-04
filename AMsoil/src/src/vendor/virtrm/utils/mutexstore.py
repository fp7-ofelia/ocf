from threading import Thread, Lock

'''
        @author: msune

        Mutex store; class that encapsulates MUTEX operations for Objects in general

'''

#static variables
localmutex = Lock()

##Composed id with project,slice and vmname     
_locks={}


class MutexStore():
    @staticmethod
    def __get_key(vm):
        return vm.project_id+vm.slice_id+vm.name
    
    @staticmethod
    def __get_lock_by_key(key):
        # This localExclusion is to prevent problems if never resources (dictionary entry) are freed in unlock method
        #print key
        localmutex.acquire()
        if not _locks.has_key(key):
            # Create Mutex for the VM
            _locks[key] = Lock()
        # Release local mutex
        localmutex.release()
        return _locks[key] 
            
    @staticmethod
    def get_object_lock(key):        
        return MutexStore.__get_lock_by_key(key)
    
    @staticmethod
    def lock(key):
        #print "Trying to lock>>>"+key
        lock = MutexStore.__get_lock_by_key(key)
        # Acquire specific VM lock
        #print "trying to acquire lock>>>"+key
        lock.acquire()
        #print "Lock acquired>>>"+key
        return
    
    @staticmethod
    def unlock(key):
        localmutex.acquire()
        # Release specific VM lock
        # TODO: release resources in dict?
        lock = MutexStore.__get_lock_by_key(key)
        lock.release()
        #print "Lock released>>>"+MutexStore.__getKey(vm)
        localmutex.release()

#print "Hola"
#l = MutexStore.getObjectLock("hola")
#d = MutexStore.getObjectLock("hola2")

#l.acquire()
#d.acquire()
#print "Hola"
#l.release()
#MutexStore.unlock("hola")
