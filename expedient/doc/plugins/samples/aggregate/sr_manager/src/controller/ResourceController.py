from settings.settingsLoader import XMLRPC_SERVER_PASSWORD

class ResourceController: 
	
    @staticmethod
    def add_resource(action_id):
        return True

    @staticmethod
    def connect(action_id):
        return "Successfully connected"

    @staticmethod
    def get_resources():
        try:
            return open("resources.xml").read()
        except:
            return ""

    @staticmethod
    def ping(challenge):
        return challenge

    @staticmethod
    def ping_auth(challenge, password):
        if password != XMLRPC_SERVER_PASSWORD:
            raise Exception("Password mismatch")
        return challenge

