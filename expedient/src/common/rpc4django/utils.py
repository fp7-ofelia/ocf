'''
Created on Jun 9, 2010

@author: jnaous
'''
from django.conf.urls.defaults import url

def rpc_url(regex, kwargs=None, name=None, prefix='',
            use_name_for_dispatch=True):
    """
    Wrapper around C{django.conf.urls.defaults.url} to add the C{name} parameter
    to C{kwargs} as "url_name", and to automatically assign the C{view}.
    C{use_name_for_dispatch} controls whether or not to add C{name} to C{kwargs}
    """
    if name != None and use_name_for_dispatch:
        if kwargs == None:
            kwargs = {}
        kwargs["url_name"] = name
    view = "expedient.common.rpc4django.views.serve_rpc_request"
    return url(regex, view, kwargs, name, prefix)
