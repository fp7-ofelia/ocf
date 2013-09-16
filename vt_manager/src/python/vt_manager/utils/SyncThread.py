from threading import Thread

class SyncThread(Thread):

    self.callBackURL = None

    def __init__(self, method, params, callBackUrl=None):
                Thread.__init__(self)
                self.method = method
                self.parms = params
		self.callBackURL = callBackUrl

        def run(self):
                self.method(*self.params)
