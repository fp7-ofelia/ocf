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

@decorator
def check_verified_user(func, *args, **kwargs):
    try:
        username = kwargs['request'].META['REMOTE_USER']
        user = User.objects.get(username=username)
    except Exception as e:
        import traceback
        traceback.print_exc()
        pprint(kwargs, indent=8)
        return "ERROR: %s: Unauthenticated user!" % func.func_name
    else:
        kwargs['user'] = user
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
                      'array', 'array'])
@check_verified_user
@get_om
def create_slice(slice_id, project_name, project_description,
                  slice_name, slice_description, controller_url,
                  owner_email, owner_password,
                  switch_slivers, **kwargs):
    print "reserve_slice got the following:"
    print "    slice_id: %s" % slice_id
    print "    project_name: %s" % project_name
    print "    project_desc: %s" % project_description
    print "    slice_name: %s" % slice_name
    print "    slice_desc: %s" % slice_description
    print "    controller: %s" % controller_url
    print "    owner_email: %s" % owner_email
    print "    owner_pass: %s" % owner_password
    
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
            switch_slivers=pformat(switch_slivers),
        ),
    )
    return {
        'error_msg': "",
        'switches': [],
    }

@rpcmethod(signature=['string', 'int'])
@check_verified_user
@get_om
def delete_slice(slice_id, **kwargs):
    slice = DummyOMSlice.objects.get(slice_id=slice_id, om=kwargs['om'])
    slice.delete()
    
    return ""

@rpcmethod(signature=['array'])
@check_verified_user
@get_om
def get_switches(**kwargs):
    return kwargs['om'].get_switches()

@rpcmethod(signature=['array'])
@check_verified_user
@get_om
def get_links(**kwargs):
    return kwargs['om'].get_links()    

@rpcmethod(signature=['string', 'string', 'string'])
@check_verified_user
@get_om
def register_topology_callback(url, cookie, **kwargs):
    print "Called register topology callback"
    attrs = {'url': url, 'cookie': cookie}
    filter_attrs = {'username': kwargs['user'].username,
                    'om': kwargs['om']}
    create_or_update(DummyCallBackProxy, filter_attrs, attrs)
    return ""

@rpcmethod(signature=['string', 'string'])
@check_verified_user
@get_om
def change_password(new_password, **kwargs):
    print"******** change_password started"
    kwargs['user'].set_password(new_password)
    kwargs['user'].save()
    print "******** change_password Done to %s" % new_password
    return ""
