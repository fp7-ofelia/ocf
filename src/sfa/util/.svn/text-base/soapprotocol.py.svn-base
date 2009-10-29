# SOAP-specific code for GeniClient

import pdb
from ZSI.client import Binding
from httplib import HTTPSConnection

def xmlrpc_like_callable (soap_callable, *x):
    soap_result = soap_callable(*x)
    xmlrpc_result = soap_result['Result']
    return xmlrpc_result
        
class SFACallable:
     def __init__(self, soap_callable):
        self.soap_callable = soap_callable

     def __call__(self, *args):
         outer_result = self.soap_callable(*args)
         return outer_result['Result']


class SFASoapBinding(Binding):
    def __getattr__(self, attr):
        soap_callable = Binding.__getattr__(self, attr)
        return SFACallable(soap_callable)


def get_server(url, key_file, cert_file):
    auth = {
        'transport' : HTTPSConnection,
        'transdict' : {'cert_file' : cert_file, 
                       'key_file' : key_file
                      },
     }

    return SFASoapBinding(url=url, **auth)

