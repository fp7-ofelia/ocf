'''
Created on May 13, 2010

@author: jnaous
'''
from expedient.common.rpc4django import rpcmethod
from django.contrib.auth.models import User
from pprint import pprint, pformat
from models import DummyOM, DummyOMSlice, DummyCallBackProxy
from expedient.common.utils import create_or_update
from decorator import decorator
from base64 import b64encode
import pickle

import logging
logger = logging.getLogger("DummyOM-API")

@decorator
def check_verified_user(func, *args, **kwargs):
    if not kwargs['request'].user.is_authenticated():
        raise Exception("ERROR: %s: Unauthenticated user!" % func.func_name)
    else:
        kwargs['user'] = kwargs['request'].user
        return func(*args, **kwargs)

@decorator
def get_om(func, *args, **kwargs):
    om_id = kwargs['om_id']
    om = DummyOM.objects.get(id=om_id)
    kwargs['om'] = om
    return func(*args, **kwargs)

@rpcmethod(signature=['struct', # return value
                      'int', 'string', 'string',
                      'string', 'string', 'string',
                      'array', 'array'],
            url_name="dummyom_rpc")
@check_verified_user
@get_om
def create_slice(slice_id, project_name, project_description,
                  slice_name, slice_description, controller_url,
                  owner_email, owner_password,
                  switch_slivers, **kwargs):
    logger.debug("reserve_slice")
    logger.debug("    slice_id: %s" % slice_id)
    logger.debug("    project_name: %s" % project_name)
    logger.debug("    project_desc: %s" % project_description)
    logger.debug("    slice_name: %s" % slice_name)
    logger.debug("    slice_desc: %s" % slice_description)
    logger.debug("    controller: %s" % controller_url)
    logger.debug("    owner_email: %s" % owner_email)
    logger.debug("    owner_pass: %s" % owner_password)
    logger.debug(pformat("    slivers: %s" % switch_slivers))
    
    # update or create the slice
    slice = create_or_update(
        DummyOMSlice,
        filter_attrs=dict(
            slice_id=slice_id,
            om=kwargs['om'],
        ),
        new_attrs=dict(
            project_name=project_name,
            project_description=project_description,
            slice_name=slice_name,
            slice_description=slice_description,
            controller_url=controller_url,
            owner_email=owner_email,
            owner_password=owner_password,
            switch_slivers=b64encode(pickle.dumps(switch_slivers)),
        ),
    )
    return {
        'error_msg': "",
        'switches': [],
    }

@rpcmethod(signature=['string', 'int'], url_name="dummyom_rpc")
@check_verified_user
@get_om
def delete_slice(slice_id, **kwargs):
    try:
        slice = DummyOMSlice.objects.get(slice_id=slice_id, om=kwargs['om'])
    except DummyOMSlice.DoesNotExist:
        pass
    else:
        slice.delete()
    
    return ""

@rpcmethod(signature=['array'], url_name="dummyom_rpc")
@check_verified_user
@get_om
def get_switches(**kwargs):
    logger.debug("Called get_switches for OM id %s" % kwargs['om'].id)
    return kwargs['om'].get_switches()

@rpcmethod(signature=['array'], url_name="dummyom_rpc")
@check_verified_user
@get_om
def get_links(**kwargs):
    logger.debug("#################Called get_links for OM id %s" % kwargs['om'].id)
    return kwargs['om'].get_links()    

@rpcmethod(signature=['string', 'string', 'string'], url_name="dummyom_rpc")
@check_verified_user
@get_om
def register_topology_callback(url, cookie, **kwargs):
    logger.debug("Called register topology callback")
    attrs = {'url': url, 'cookie': cookie}
    filter_attrs = {'username': kwargs['user'].username,
                    'om': kwargs['om']}
    create_or_update(DummyCallBackProxy, filter_attrs, attrs)
    return ""

@rpcmethod(signature=['string', 'string'], url_name="dummyom_rpc")
@check_verified_user
@get_om
def change_password(new_password, **kwargs):
    logger.debug("******** change_password started")
    kwargs['user'].set_password(new_password)
    kwargs['user'].save()
    logger.debug("******** change_password Done to %s" % new_password)
    return ""

@check_verified_user
@rpcmethod(signature=['string', 'string'], url_name="dummyom_rpc")
def ping(data, **kwargs):
    '''
    Test method to see that everything is up.
    return a string that is "PONG: %s" % data
    '''
    logger.debug("Pinged!")
    return "PONG: %s" % data
