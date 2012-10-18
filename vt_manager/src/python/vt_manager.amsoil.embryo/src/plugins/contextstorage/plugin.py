"""
Represents a storage for a _request_.
The RPC plugin should create a context/initialize a new context when a new requets comes in.
The context module enforces the presence of a user_id, rpc_type and rpc_version like so:
    import amsoil.core.pluginmanager as pm
    contextKlass = pm.getService('context')
    context = contextKlass('some_user_id_from_the_request', 'geni', 2)

Other plugins can then access that storage and add/read data to a dictionary:
    context = pm.getService('context').currentContext()
    uid = context.user_id
    context.data['xyz'] = 'someval'
    ...
    myval = context.data['xyz']
"""

import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('context')

from cs.contextstorage import ContextStorage

def setup():
    pm.registerService('context', ContextStorage)