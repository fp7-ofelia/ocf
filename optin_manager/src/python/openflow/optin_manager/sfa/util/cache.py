#
# This module implements general purpose caching system
#
from __future__ import with_statement
import time
import threading
import pickle
from datetime import datetime

# maximum lifetime of cached data (in seconds) 
DEFAULT_CACHE_TTL = 60 * 60

class CacheData:

    data = None
    created = None
    expires = None
    lock = None

    def __init__(self, data, ttl = DEFAULT_CACHE_TTL):
        self.lock = threading.RLock()
        self.data = data
        self.renew(ttl)

    def is_expired(self):
        return time.time() > self.expires

    def get_created_date(self):
        return str(datetime.fromtimestamp(self.created))

    def get_expires_date(self):
        return str(datetime.fromtimestamp(self.expires))

    def renew(self, ttl = DEFAULT_CACHE_TTL):
        self.created = time.time()
        self.expires = self.created + ttl   
       
    def set_data(self, data, renew=True, ttl = DEFAULT_CACHE_TTL):
        with self.lock: 
            self.data = data
            if renew:
                self.renew(ttl)
    
    def get_data(self):
        return self.data


    def dump(self):
        return self.__dict__

    def __str__(self):
        return str(self.dump())  
        
    def tostring(self):
        return self.__str__()

    def __getstate__(self):
        d = dict(self.__dict__)
        del d['lock']
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
        self.lock = threading.RLock()
        

class Cache:

    cache  = {}
    lock = threading.RLock()

    def __init__(self, filename=None):
        if filename:
            self.load_from_file(filename)
   
    def add(self, key, value, ttl = DEFAULT_CACHE_TTL):
        with self.lock:
            if self.cache.has_key(key):
                self.cache[key].set_data(value, ttl=ttl)
            else:
                self.cache[key] = CacheData(value, ttl)
           
    def get(self, key):
        data = self.cache.get(key)
        if not data:  
            data = None
        elif data.is_expired():
            self.pop(key)
            data = None 
        else:
            data = data.get_data()
        return data

    def pop(self, key):
        if key in self.cache:
            self.cache.pop(key) 

    def dump(self):
        result = {}
        for key in self.cache:
            result[key] = self.cache[key].__getstate__()
        return result

    def __str__(self):
        return str(self.dump())     
 
    def tostring(self):
        return self.__str()    

    def save_to_file(self, filename):
        f = open(filename, 'w')
        pickle.dump(self.cache, f)

    def load_from_file(self, filename):
        f = open(filename, 'r')
        self.cache = pickle.load(f)
