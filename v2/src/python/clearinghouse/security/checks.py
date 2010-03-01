'''
Created on Feb 28, 2010

@author: jnaous

@summary: implements all the security checks
'''

#def _func_role_signals(func, sender=None):
#    from django.db.models.signals import pre_save, pre_delete
#    getattr(pre_save, func)(_check_role_save, sender=sender)
#    getattr(pre_delete, func)(_check_role_delete, sender=sender)    
#    
#def _check_role_save(sender, **kwargs):
#    '''Everytime the roles corresponding to a model change make sure the user
#    is allowed to make the change.'''
#    
#    from clearinghouse.middleware import threadlocals
#
#    curr_role = kwargs['instance']
#    user = threadlocals.get_current_user()
#    SecurityRole = sender
#    
#    print "***** CHeck role save"
#
#    # get the old role from the db
#    try:
#        old_role = SecurityRole.objects.get(pk=curr_role.pk)
#        is_new = False
#    except SecurityRole.DoesNotExist:
#        is_new = True
#    
#    if not is_new:
#        # check if the user can remove the old role from the old object
#        user_roles = old_role._object.security_roles.filter(_user=user)
#        for r in user_roles.all():
#            r = r.as_leaf_class()
#            if not r.can_delete_role(old_role):
#                raise old_role._object.__class__.SecurityException(user,
#                    "Cannot delete role %s" % old_role)
#    
#    # check if the user can add this role to the new object
#    user_roles = curr_role._object.security_roles.filter(_user=user)
#    for r in user_roles.all():
#        r = r.as_leaf_class()
#        if not r.can_add_role(curr_role):
#            raise curr_role._object.__class__.SecurityException(user,
#                "Cannot add role %s" % curr_role)
#    
#    print "***** Done check role save"
#    
#def _check_role_delete(sender, **kwargs):
#    '''Check if the user is allowed to delete the role.'''
#    
#    from clearinghouse.middleware import threadlocals
#    
#    old_role = kwargs['instance']
#    user = threadlocals.get_current_user()
#
#    user_roles = old_role._object.security_roles.filter(_user=user)
#    for r in user_roles.all():
#        r = r.as_leaf_class()
#        if not r.can_delete_role(old_role):
#            raise old_role._object.__class__.SecurityException(user,
#                "Cannot delete role %s" % old_role)
#
#def _connect_role_signals(sender=None):
##    print "Connecting signals for %s" % sender
#    _func_role_signals('connect', sender)
#    
#def _disconnect_role_signals(sender=None):
##    print "Disconnecting signals for %s" % sender
#    _func_role_signals('disconnect', sender)
#
#def _create_role_class(name, bases, dict):
#    '''Create a new class and call _connect_role_signals for it. Used internally'''
##    print "***called meta: %s %s %s" % (name, bases, dict)
#    cls = models.Model.__metaclass__(name, bases, dict)
##    print "created class %s" % cls
#    _connect_role_signals(cls)
#    return cls

#def _check_obj_save(sender, **kwargs):
#    '''
#    Get the old copy of the object, and send it to the security role
#    to ask if the current copy has any fields that are write-protected.
#    '''
#    
#    from clearinghouse.middleware import threadlocals
#    
#    SecureModel = sender
#    
#    curr_obj = kwargs['instance']
#    
#    print "Checking object %s save" % curr_obj
#    
#    # get the user
#    user = threadlocals.get_current_user()
#    
#    # Otherwise, get the SecurityRoles associated with this object
#    # and the current user
#    roles = curr_obj.security_roles.filter(_user=user)
#
#    # get the old object from the db
#    try:
#        old_obj = curr_obj.__class__.objects.get(pk=curr_obj.pk)
#    except SecureModel.DoesNotExist:
#        # The object is not in the database to begin with.
#        return
##    except AttributeError:
##        print "Saving instance %s for the first time" % curr_obj
##        return
#        
#    # check if there are no roles, so we need to check protect_roleless_objects
#    if len(roles) == 0 and curr_obj.__class__.objects.protect_roleless_objects:
#        return
#    
#    # now get what each role doesn't allow to write, and see if
#    # the intersection is empty => write is allowed by union of roles
#    disallowed_fields = set(curr_obj._meta.fields)
#    for role in roles.all():
#        role = role.as_leaf_class()
#        disallowed_fields.intersection_update(
#            set(role.get_write_protected_fields(old_obj)))
#    
#    if len(disallowed_fields) > 0:
#        vals = [curr_obj.get_attr(f) for f in disallowed_fields]
#        raise curr_obj.__class__.SecurityException(user, "Writing to fields %s"
#                " with the values %s not allowed" % (disallowed_fields, vals))
#
#    print "Done checking object %s save" % curr_obj
#
#def _check_obj_delete(sender, **kwargs):
#    '''Only allow the delete if the user is allowed to delete the object'''
#    
#    from clearinghouse.middleware import threadlocals
#    
#    curr_obj = kwargs['instance']
#    user = threadlocals.get_current_user()
#    
#    # get the current user's roles
#    roles = curr_obj.security_roles.filter(_user=user)
#    
#    for role in roles.all():
#        if role.can_delete():
#            return
#        
#    raise curr_obj.__class__.SecurityException(user, "Deleting object %s"
#                " is not allowed" % curr_obj)
#
#def _add_ownership_role(sender, **kwargs):
#    '''If the object was just created and protect_roleless_objects is set, then
#    give the current user as an OwnerSecurityRole'''
#
#    from clearinghouse.middleware import threadlocals
#    
#    curr_obj = kwargs['instance']
#    print "called _add_ownership_role to obj %s" % curr_obj
#
#    if kwargs['created'] and curr_obj.__class__.objects.protect_roleless_objects:
#        # add an ownership role to the user for this object
#        user = threadlocals.get_current_user()
#        if user:
#            threadlocals.push_admin_mode()
#            OwnerSecurityRole.objects.create(_user=user, _object=curr_obj)
#            threadlocals.pop_admin_mode()
#
#def _func_obj_signals(func, sender=None):
#    from django.db.models.signals import pre_save, post_save, pre_delete
#    getattr(pre_save, func)(_check_obj_save, sender=sender)
#    getattr(pre_delete, func)(_check_obj_delete, sender=sender)
#    getattr(post_save, func)(_add_ownership_role, sender=sender)
#    
#def _connect_obj_signals(sender=None):
##    print "Connecting signals for %s" % sender
#    _func_obj_signals('connect', sender)
#    
#def _disconnect_obj_signals(sender=None):
##    print "Disconnecting signals for %s" % sender
#    _func_obj_signals('disconnect', sender)


def connect_all_signals():
    pass
#    print "Connecting signals:"

#    # Get all successors of SecureModel
#    obj_successors = utils.itersubclasses(SecureModel)
#    for s in obj_successors:
##        print "    for %s" % s
#        _connect_obj_signals(s)
#        
#    role_successors = utils.itersubclasses(SecurityRole)
#    for s in role_successors:
##        print "    for %s" % s
#        _connect_role_signals(s)

def disconnect_all_signals():
    pass
##    print "Disconnecting signals:"
#
#    # Get all successors of SecureModel
#    obj_successors = utils.itersubclasses(SecureModel)
#    for s in obj_successors:
##        print "    for %s" % s
#        _disconnect_obj_signals(s)
#        
#    role_successors = utils.itersubclasses(SecurityRole)
#    for s in role_successors:
##        print "    for %s" % s
#        _disconnect_role_signals(s)
