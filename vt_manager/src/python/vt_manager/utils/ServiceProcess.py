from multiprocessing import Process

class ServiceProcess(Process):

        __method = None
        __param = None
        callBackURL=None
        event = None

        @staticmethod
        def startMethodInNewProcess(servmethod,param,url = None):
                thread = ServiceProcess()
                thread.callBackURL = url
                thread.startMethod(servmethod,param,url)
        def startMethod(self,servmethod,param,url):
                self.__method = servmethod
                self.__param = param
		callBackURL = url
                self.start()

        def run(self):
                self.__method(self.__param, self.callBackURL)

