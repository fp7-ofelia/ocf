#!/usr/bin/python

import threading
import time

#from foam.sfa.util.sfalogging import logger

"""
Callids: a simple mechanism to remember the call ids served so fas
memory-only for now - thread-safe
implemented as a (singleton) hash 'callid'->timestamp
"""

debug=False

class _call_ids_impl (dict):

    _instance = None
    # 5 minutes sounds amply enough
    purge_timeout=5*60
    # when trying to get a lock
    retries=10
    # in ms
    wait_ms=100

    def __init__(self): 
        self._lock=threading.Lock()

    # the only primitive
    # return True if the callid is unknown, False otherwise
    def already_handled (self,call_id):
        # if not provided in the call...
        if not call_id: return False
        has_lock=False
        for attempt in range(_call_ids_impl.retries):
            if debug: logger.debug("Waiting for lock (%d)"%attempt)
            if self._lock.acquire(False): 
                has_lock=True
                if debug: logger.debug("got lock (%d)"%attempt)
                break
            time.sleep(float(_call_ids_impl.wait_ms)/1000)
        # in the unlikely event where we can't get the lock
        if not has_lock:
            logger.warning("_call_ids_impl.should_handle_call_id: could not acquire lock")
            return False
        # we're good to go
        if self.has_key(call_id):
            self._purge()
            self._lock.release()
            return True
        self[call_id]=time.time()
        self._purge()
        self._lock.release()
        if debug: logger.debug("released lock")
        return False
        
    def _purge(self):
        now=time.time()
        o_keys=[]
        for (k,v) in self.iteritems():
            if (now-v) >= _call_ids_impl.purge_timeout: o_keys.append(k)
        for k in o_keys: 
            if debug: logger.debug("Purging call_id %r (%s)"%(k,time.strftime("%H:%M:%S",time.localtime(self[k]))))
            del self[k]
        if debug:
            logger.debug("AFTER PURGE")
            for (k,v) in self.iteritems(): logger.debug("%s -> %s"%(k,time.strftime("%H:%M:%S",time.localtime(v))))
        
def Callids ():
    if not _call_ids_impl._instance:
        _call_ids_impl._instance = _call_ids_impl()
    return _call_ids_impl._instance
