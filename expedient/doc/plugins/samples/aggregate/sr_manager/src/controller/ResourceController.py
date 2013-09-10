"""
Implements the functionality for those methods defined
in XmlRpcAPI.

@date: Jun 12, 2013
@author: CarolinaFernandez
"""

from settings import XMLRPC_SERVER_PASSWORD

class ResourceController: 
	
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

