from django.db import models
from django.contrib import auth
from clearinghouse.security import utils
from django.contrib.contenttypes.models import ContentType
from django.db.models.base import ModelBase

def _func_role_signals(func, sender=None):
    from django.db.models.signals import pre_save, pre_delete
    getattr(pre_save, func)(_check_role_save, sender=sender)
    getattr(pre_delete, func)(_check_role_delete, sender=sender)    
    
def _check_role_save(sender, **kwargs):
    '''Everytime the roles corresponding to a model change make sure the user
    is allowed to make the change.'''
    
    from clearinghouse.middleware import threadlocals

    curr_role = kwargs['instance']
    user = threadlocals.get_current_user()
    SecurityRole = sender
    
    print "***** CHeck role save"

    # get the old role from the db
    try:
        old_role = SecurityRole.objects.get(pk=curr_role.pk)
        is_new = False
    except SecurityRole.DoesNotExist:
        is_new = True
    
    if not is_new:
        # check if the user can remove the old role from the old object
        user_roles = old_role._object.security_roles.filter(_user=user)
        for r in user_roles.all():
            r = r.as_leaf_class()
            if not r.can_delete_role(old_role):
                raise old_role._object.__class__.SecurityException(user,
                    "Cannot delete role %s" % old_role)
    
    # check if the user can add this role to the new object
    user_roles = curr_role._object.security_roles.filter(_user=user)
    for r in user_roles.all():
        r = r.as_leaf_class()
        if not r.can_add_role(curr_role):
            raise curr_role._object.__class__.SecurityException(user,
                "Cannot add role %s" % curr_role)
    
    print "***** Done check role save"
    
def _check_role_delete(sender, **kwargs):
    '''Check if the user is allowed to delete the role.'''
    
    from clearinghouse.middleware import threadlocals
    
    old_role = kwargs['instance']
    user = threadlocals.get_current_user()

    user_roles = old_role._object.security_roles.filter(_user=user)
    for r in user_roles.all():
        r = r.as_leaf_class()
        if not r.can_delete_role(old_role):
            raise old_role._object.__class__.SecurityException(user,
                "Cannot delete role %s" % old_role)

def _connect_role_signals(sender=None):
#    print "Connecting signals for %s" % sender
    _func_role_signals('connect', sender)
    
def _disconnect_role_signals(sender=None):
#    print "Disconnecting signals for %s" % sender
    _func_role_signals('disconnect', sender)

def _create_role_class(name, bases, dict):
    '''Create a new class and call _connect_role_signals for it. Used internally'''
#    print "***called meta: %s %s %s" % (name, bases, dict)
    cls = models.Model.__metaclass__(name, bases, dict)
#    print "created class %s" % cls
    _connect_role_signals(cls)
    return cls

class SecurityRoleMetaClass(ModelBase):
    def __new__(cls, name, bases, dict):
        print "called meta: %s %s %s" % (name, bases, dict)
        
        # get the related model first
        if 'Meta' in dict:
            meta = dict['Meta']
            fld = 'related_secure_model'
            related = getattr(meta, fld, 'SecureModel')
            del meta.__dict__[fld]
            
            # add a _object field pointing to the role
            dict['_object'] = models.ForeignKey(related, related_name='security_roles')
        
        # Create the class
        cls = super(SecurityRoleMetaClass, cls).__new__(cls, name, bases, dict)
#        print "created class %s" % cls
        _connect_role_signals(cls)
        return cls

#class BaseSecurityRole(models.Model):
class SecurityRole(models.Model):
    '''
    Defines the relationship of every object to every user.
    By default, not all users can see/modify all SecureModel objects.
    '''
    
    _user = models.ForeignKey(auth.models.User, related_name='security_roles')
    _object = models.ForeignKey('SecureModel', related_name='security_roles')
    
    content_type = models.ForeignKey(ContentType, editable=False, null=True)
    
    __metaclass__ = SecurityRoleMetaClass
    
    def __unicode__(self):
        return "Role: %s, user: %s, object: %s" % (self.__class__,
                                                   self._user,
                                                   self._object)

    def save(self, *args, **kwargs):
        if(not self.content_type):
            self.content_type = ContentType.objects.get_for_model(self.__class__)
#        super(BaseSecurityRole, self).save(*args, **kwargs)
        super(SecurityRole, self).save(*args, **kwargs)
        
    def as_leaf_class(self):
#        return self
        content_type = self.content_type
        model = content_type.model_class()
#        if(model == BaseSecurityRole):
        if(model == SecurityRole):
            return self
        return model.objects.get(id=self.id)
    
    def get_write_protected_fields(self, old_object):
        '''
        compare the old and current (self._object) copies of the object
        and return a list of the field names that should not be allowed
        to be written or whose modifications are not allowed by the user.
        
        Parameters:
        @param old_object -- the object currently in the database unmodified
            
        Return:
        @return list of disallowed fields
        '''
        raise NotImplementedError
    
    def get_read_protected_fields(self):
        '''
        Return a list of the fields that the user is not allowed to see.
        Note that if the values for read-protected fields are modified, a
        SecurityException will be raised.

        Return:
        @return list of secret fields
        '''
        raise NotImplementedError
    
    def can_delete(self):
        '''
        Does this role allow self._user to delete the object?

        Return:
        @return True if allowed False otherwise.
        '''
        raise NotImplementedError
    
    def can_add_role(self, role):
        '''
        Does this role allow self._user to add the role 'role'?

        Parameters:
        @param role -- the SecurityRole which is to be given to user

        Return:
        @return True if allowed False otherwise.
        '''
        raise NotImplementedError
    
    def can_delete_role(self, role):
        '''
        Does this role allow self._user to remove the role 'role'?

        Parameters:
        @param role -- the SecurityRole from which a role is being removed

        Return:
        @return True if allowed False otherwise.
        '''
        raise NotImplementedError

#class SecurityRole(BaseSecurityRole):
#    pass

class OwnerSecurityRole(SecurityRole):
    '''Default role assigned to the owner of a newly created object'''
    
#    classes = ['SecureModel']
    
    def get_write_protected_fields(self, old_object):
        return []
    
    def get_read_protected_fields(self):
        return []
    
    def can_delete(self):
        return True
    
    def can_add_role(self, role):
        return True
    
    def can_delete_role(self, role):
        return True

################################################################################
# Now the SecureModel Code
#

#def secure_class_prepared_handler(sender, **kwargs):
#    '''Make sure that 'classes' is defined as an attribute in all
#    SecurityRole children, and count the successors for SecureModel'''
#     
#    if SecurityRole in sender.mro():
#        # check that classes is defined
#        if 'classes' not in sender.__dict__:
#            raise Exception("You need to define a 'classes' attribute in "+
#                "SecurityRole child %s" % sender)
        
class SecureModelManager(models.Manager):
    '''
    Default Manager class for SecureModel subclasses. Mainly used
    to restrict the returned QuerySet
    '''

    use_for_related_fields = True
    
    def __init__(self, *args, **kwargs):

#        from django.db.models.signals import class_prepared

        super(SecureModelManager, self).__init__(*args, **kwargs)

        # by default don't give users with unknown roles
        # any access to an object.
        self.protect_roleless_objects = True
        
        # connect the signal to check that SecureModel children are correct
#        class_prepared.connect(secure_class_prepared_handler)
        
    def get_query_set(self):
        '''
        Return a filtered QuerySet, with objects that are not allowed
        to be seen filtered out.
        
        @return the filtered QuerySet instance
        '''
        from clearinghouse.security.query import SecureQuerySet
        
        # the full query set
        return SecureQuerySet(
            self.model,
            protect_roleless_objects=self.protect_roleless_objects)

def _check_obj_save(sender, **kwargs):
    '''
    Get the old copy of the object, and send it to the security role
    to ask if the current copy has any fields that are write-protected.
    '''
    
    from clearinghouse.middleware import threadlocals
    
    SecureModel = sender
    
    curr_obj = kwargs['instance']
    
    print "Checking object %s save" % curr_obj
    
    # get the user
    user = threadlocals.get_current_user()
    
    # Otherwise, get the SecurityRoles associated with this object
    # and the current user
    roles = curr_obj.security_roles.filter(_user=user)

    # get the old object from the db
    try:
        old_obj = curr_obj.__class__.objects.get(pk=curr_obj.pk)
    except SecureModel.DoesNotExist:
        # The object is not in the database to begin with.
        return
#    except AttributeError:
#        print "Saving instance %s for the first time" % curr_obj
#        return
        
    # check if there are no roles, so we need to check protect_roleless_objects
    if len(roles) == 0 and curr_obj.__class__.objects.protect_roleless_objects:
        return
    
    # now get what each role doesn't allow to write, and see if
    # the intersection is empty => write is allowed by union of roles
    disallowed_fields = set(curr_obj._meta.fields)
    for role in roles.all():
        role = role.as_leaf_class()
        disallowed_fields.intersection_update(
            set(role.get_write_protected_fields(old_obj)))
    
    if len(disallowed_fields) > 0:
        vals = [curr_obj.get_attr(f) for f in disallowed_fields]
        raise curr_obj.__class__.SecurityException(user, "Writing to fields %s"
                " with the values %s not allowed" % (disallowed_fields, vals))

    print "Done checking object %s save" % curr_obj

def _check_obj_delete(sender, **kwargs):
    '''Only allow the delete if the user is allowed to delete the object'''
    
    from clearinghouse.middleware import threadlocals
    
    curr_obj = kwargs['instance']
    user = threadlocals.get_current_user()
    
    # get the current user's roles
    roles = curr_obj.security_roles.filter(_user=user)
    
    for role in roles.all():
        if role.can_delete():
            return
        
    raise curr_obj.__class__.SecurityException(user, "Deleting object %s"
                " is not allowed" % curr_obj)

def _add_ownership_role(sender, **kwargs):
    '''If the object was just created and protect_roleless_objects is set, then
    give the current user as an OwnerSecurityRole'''

    from clearinghouse.middleware import threadlocals
    
    curr_obj = kwargs['instance']
    print "called _add_ownership_role to obj %s" % curr_obj

    if kwargs['created'] and curr_obj.__class__.objects.protect_roleless_objects:
        # add an ownership role to the user for this object
        user = threadlocals.get_current_user()
        if user:
            threadlocals.push_admin_mode()
            OwnerSecurityRole.objects.create(_user=user, _object=curr_obj)
            threadlocals.pop_admin_mode()

def _func_obj_signals(func, sender=None):
    from django.db.models.signals import pre_save, post_save, pre_delete
    getattr(pre_save, func)(_check_obj_save, sender=sender)
    getattr(pre_delete, func)(_check_obj_delete, sender=sender)
    getattr(post_save, func)(_add_ownership_role, sender=sender)
    
def _connect_obj_signals(sender=None):
#    print "Connecting signals for %s" % sender
    _func_obj_signals('connect', sender)
    
def _disconnect_obj_signals(sender=None):
#    print "Disconnecting signals for %s" % sender
    _func_obj_signals('disconnect', sender)

def _create_model_class(name, bases, dict):
    '''Create a new class and call _connect_obj_signals for it. Used internally.'''
#    print "called meta: %s %s %s" % (name, bases, dict)
    cls = ModelBase(name, bases, dict)
#    print "created class %s" % cls
    _connect_obj_signals(cls)
    return cls

class SecureModelMetaClass(ModelBase):
    def __new__(cls, name, bases, dict):
#        print "called meta: %s %s %s" % (name, bases, dict)
        cls = super(SecureModelMetaClass, cls).__new__(cls, name, bases, dict)
#        print "created class %s" % cls
        _connect_obj_signals(cls)
        return cls
    
class AbstractSecureModel(models.Model):
    '''
    Define the default Manager in an abstract class so that
    it gets inherited in all successors in the inheritance hierarchy
    as defined by Django's Manage inheritance rules.
    '''
    objects = SecureModelManager()
    
    __metaclass__ = SecureModelMetaClass

    class Meta:
        abstract = True

class SecureModel(AbstractSecureModel):
    '''
    All models that want to use the advanced permissions
    from the security app need to inherit from SecureModel.
    '''
    
    _obj_users = models.ManyToManyField(auth.models.User,
                                        through='SecurityRole')
    
#    content_type = models.ForeignKey(ContentType, editable=False, null=True)
#    
#    def save(self, *args, **kwargs):
#        if(not self.content_type):
#            self.content_type = ContentType.objects.get_for_model(self.__class__)
#        super(SecureModel, self).save(*args, **kwargs)
#        
#    def as_leaf_class(self):
#        content_type = self.content_type
#        model = content_type.model_class()
#        if(model == SecureModel):
#            return self
#        return model.objects.get(id=self.id)

    class SecurityException(Exception):
        '''Exceptions caused by the security app for this model
        
        Attributes:
        @param user -- user who caused the exception
        @param msg -- explanation of the exception
        '''
        def __init__(self, user, msg):
            self.user = user
            self.msg = msg
    
def connect_all_signals():
#    print "Connecting signals:"

    # Get all successors of SecureModel
    obj_successors = utils.itersubclasses(SecureModel)
    for s in obj_successors:
#        print "    for %s" % s
        _connect_obj_signals(s)
        
    role_successors = utils.itersubclasses(SecurityRole)
    for s in role_successors:
#        print "    for %s" % s
        _connect_role_signals(s)

def disconnect_all_signals():
#    print "Disconnecting signals:"

    # Get all successors of SecureModel
    obj_successors = utils.itersubclasses(SecureModel)
    for s in obj_successors:
#        print "    for %s" % s
        _disconnect_obj_signals(s)
        
    role_successors = utils.itersubclasses(SecurityRole)
    for s in role_successors:
#        print "    for %s" % s
        _disconnect_role_signals(s)

# NOTES:
# Models should not be defined with unique columns that are secret. Otherwise,
# when adding a new instance, the values might not be unique.
#
# Need to make sure to set the correct current user for ownership or to remove
# the ownership after adding and set the right roles

# TODO: Solve the __metaclass__ inheritance issue
# TODO: Solve the inheritance issue where looking up roles gives generic SecurityRole objects.
