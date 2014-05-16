from threading import Thread

class ServiceThread(Thread):
    
    __method = None        
    __param = None
    callback_url=None
    
    @staticmethod
    def start_method_in_new_thread(servmethod,param,url = None):
        thread = ServiceThread()        
        thread.callback_url = url
        thread.start_method(servmethod,param)
    
    def start_method(self,servmethod,param):
        self.__method = servmethod
        self.__param = param
        self.start()
    
    def run(self):        
        self.__method(self.__param)                        
