from AuthenticatedApi import AuthenticatedApi, BadRequestHash

class RemoteApi(AuthenticatedApi):
    def __init__(self, encoding="utf-8", trustedRootsDir="/usr/local/testapi/var/trusted_roots"):
        return AuthenticatedApi.__init__(self, encoding)

    def get_log_name(self):
        return "/usr/local/testapi/var/logfile.txt"

    def register_functions(self):
        AuthenticatedApi.register_functions(self)
        self.register_function(self.typeError)
        self.register_function(self.badRequestHash)

    def typeError(self):
        raise TypeError()

    def badRequestHash(self):
        raise BadRequestHash("somehashvalue")
