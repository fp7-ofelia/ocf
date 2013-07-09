"""
Defines the dummy AM API.

@date: Jun 12, 2013
@author: CarolinaFernandez
"""

from controller.ResourceController import ResourceController
import string

class xmlrpc_wrappers:
    """
    Allowed methods on the XMLRPC server
    """

    def __init__(self, callback_function = None):
        self.callback_function = callback_function

    def get_resources(self):
        return ResourceController.get_resources()

    def ping_auth(self, challenge, password):
        return ResourceController.ping_auth(challenge, password)

    def ping(self, challenge):
        return ResourceController.ping(challenge)

