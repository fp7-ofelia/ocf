class Generic:

    def __init__(self, backend, api_type):

        self.backend = backend
        self.api_type = api_type

    def get_info(self):
        print 'API: %s \n Backend: %s' %(self.api_type, self.backend)

    @staticmethod
    def make_api(backend, api_type):
        return Generic(persistence,api_type)

    def get_bakend(self):
        return self.backend

    def get_api_type(self):
        return self.api_type

    def set_backend(self, backend):
        self.backend = backend

    def set_api_type(self, api_type):
        self.api_type = api_type
