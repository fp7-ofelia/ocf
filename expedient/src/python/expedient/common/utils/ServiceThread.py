from threading import Thread

class ServiceThread(Thread):

    __method = None
    __params = None
    callback_url = None
    request_user = None

    @staticmethod
    def start_method_new_thread(method, request_user = None, url = None, *params):
        thread = ServiceThread()
        # Add this 2 params if != None
        if request_user:
            thread.request_user = request_user
        if url:
            thread.callback_url = url
        thread.start_method(method, *params)

    def start_method(self, method, *params):
        self.__method = method
        self.__params = params
        self.start()

    def run(self):
        # self.__params is a tuple of arguments. The asterisk ("*")
        # converts this tuple into a series of arguments
        self.__method(*self.__params)

