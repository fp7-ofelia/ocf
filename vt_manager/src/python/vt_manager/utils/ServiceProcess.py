from multiprocessing import Process

class ServiceProcess(Process):

        __method = None
        __params = list()
        callBackURL=None
        event = None

        @staticmethod
        def startMethodInNewProcess(servmethod,params,url = None):
                thread = ServiceProcess()
                thread.callBackURL = url
                thread.startMethod(servmethod,params,url)
        def startMethod(self,servmethod,params,url):
                self.__method = servmethod
                self.__params = params
		callBackURL = url
                self.start()

        def run(self):
		if not isinstance(self.__params,list):
			self.__params = [params]
                self.__method(*self.__params)

