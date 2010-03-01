'''
Created on Feb 28, 2010

@author: jnaous

@summary: implements all the security checks

@TODO: Make the checking have both con/disjunctions
@TODO: Check that the parents' security permissions are good too
'''
from clearinghouse.middleware import threadlocals
from clearinghouse.security import utils, models

def _check_role_delete(sender, **kwargs):
    '''Check if the user is allowed to delete the role.'''
    
    old_role = kwargs['instance']
    user = threadlocals.get_current_user()

    user_roles = old_role.security_object.\
        security_base_role_class.get_roles_for_user(user)
    
    for r in user_roles:
        if not r.can_del_role(old_role.security_object,
                              old_role.get_role(),
                              old_role.security_user):
            raise old_role.security_object.SecurityException(user,
                    "Cannot delete role %s" % old_role)
    
def _check_role_save(sender, **kwargs):
    '''Everytime the roles corresponding to a model change make sure the user
    is allowed to make the change.'''
    
    curr_role = kwargs['instance']
    user = threadlocals.get_current_user()
    SecurityRole = sender
    
    print "***** Check role save"

    # get the old role from the db
    try:
        old_role = SecurityRole.objects.get(pk=curr_role.pk)
    except SecurityRole.DoesNotExist:
        pass
    else:
        # check if the user can remove the old role from the old object
        _check_role_delete(sender, {'instance': old_role})

    # check if the user can add this role to the new object
    user_roles = curr_role.security_object.\
        security_base_role_class.get_roles_for_user(user)
    
    for r in user_roles:
        if not r.can_add_role(curr_role.security_object,
                              curr_role.get_role(),
                              curr_role.security_user):
            raise curr_role.security_object.SecurityException(user,
                    "Cannot add role %s" % curr_role)
    
    print "***** Done check role save"

def _check_obj_save(sender, **kwargs):
    '''
    Get the old copy of the object, and send it to the security role
    to ask if the current copy has any fields that are write-protected.
    '''
    
    SecureModel = sender
    
    curr_obj = kwargs['instance']
    
    print "Checking object %s save" % curr_obj
    
    # get the user
    user = threadlocals.get_current_user()
    
    # Otherwise, get the SecurityRoles associated with this object
    # and the current user
    roles = curr_obj.security_base_role_class.get_roles_for_user(user)

    # get the old object from the db
    try:
        old_obj = curr_obj.objects.get(pk=curr_obj.pk)
    except SecureModel.DoesNotExist:
        # The object is not in the database to begin with.
        return
#    except AttributeError:
#        print "Saving instance %s for the first time" % curr_obj
#        return
        
    # check if there are no roles, so we need to check protect_roleless_objects
    if len(roles) == 0 and curr_obj.objects.protect_roleless_objects:
        return
    
    # now get what each role doesn't allow to write, and see if
    # the intersection is empty => write is allowed by union of roles
    disallowed_fields = set(curr_obj._meta.fields)
    write_allowed = True
    for role in roles:
        write_allowed = write_allowed and role.can_write(old_obj)
        disallowed_fields.intersection_update(
            set(role.get_write_protected_fields(curr_obj, old_obj)))
    
    if not write_allowed:
        raise curr_obj.SecurityException(user, 
                "Writing to object %s not allowed." % old_obj)
        
    if len(disallowed_fields) > 0:
        vals = [curr_obj.get_attr(f) for f in disallowed_fields]
        raise curr_obj.SecurityException(user, "Writing to fields %s"
                " with the values %s not allowed" % (disallowed_fields, vals))

    print "Done checking object %s save" % curr_obj

def _check_obj_delete(sender, **kwargs):
    '''Only allow the delete if the user is allowed to delete the object'''
    
    curr_obj = kwargs['instance']
    user = threadlocals.get_current_user()
    
    # get the current user's roles
    roles = curr_obj.security_base_role_class.get_roles_for_user(user)
    
    for role in roles:
        if role.can_delete(curr_obj):
            return
        
    raise curr_obj.SecurityException(user, "Deleting object %s"
                " is not allowed" % curr_obj)

def _add_ownership_role(sender, **kwargs):
    '''If the object was just created and protect_roleless_objects is set, then
    give the current user as an Owner role'''

    curr_obj = kwargs['instance']
    print "called _add_ownership_role to obj %s" % curr_obj

    if kwargs['created'] and curr_obj.objects.protect_roleless_objects:
        # add an ownership role to the user for this object
        user = threadlocals.get_current_user()
        if user:
            push_admin_mode()
            curr_obj.security_base_role_class.objects.create(
                security_user=user, security_object=curr_obj,
                security_role_choice='Owner')
            pop_admin_mode()

def _create_model_signal_funcs(func, model):
    '''Connect/Disconnect signals for role and objects'''
    
    assert(func is 'connect' or func is 'disconnect')
    assert(model is 'role' or model is 'obj')
    
    from django.db.models.signals import pre_save, pre_delete, post_save
    if model is 'role':
        def new_f(sender=None):
            getattr(pre_save, func)(_check_role_save, sender=sender)
            getattr(pre_delete, func)(_check_role_delete, sender=sender)
    else: # model is 'obj'
        def new_f(sender=None):
            getattr(pre_save, func)(_check_obj_save, sender=sender)
            getattr(pre_delete, func)(_check_obj_delete, sender=sender)
            getattr(post_save, func)(_add_ownership_role, sender=sender)
    return new_f    
    
# Create functions to connect/disconnect role and object signals
for func in ['connect', 'disconnect']:
    for model in ['role', 'obj']:
        locals()['_%s_%s_signals' % (func, model)] = _create_model_signal_funcs(func, model)

def connect_all_signals():
    # Get all successors of SecureModel
    obj_successors = utils.itersubclasses(models.AbstractSecureModel)
    for s in obj_successors:
        _connect_obj_signals(s)
        
    role_successors = utils.itersubclasses(models.BaseAbstractRole)
    for s in role_successors:
        _connect_role_signals(s)

def disconnect_all_signals():
    # Get all successors of SecureModel
    obj_successors = utils.itersubclasses(models.AbstractSecureModel)
    for s in obj_successors:
        _disconnect_obj_signals(s)
        
    role_successors = utils.itersubclasses(models.BaseAbstractRole)
    for s in role_successors:
        _disconnect_role_signals(s)

def push_admin_mode():
    disconnect_all_signals()
    threadlocals.push_obj(True)
    
def pop_admin_mode():
    threadlocals.pop_obj()
    connect_all_signals()
