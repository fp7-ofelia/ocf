from django.db import models
from django.contrib import auth
from django.db.models.base import ModelBase
from types import ClassType
from django.db.models.signals import class_prepared

def print_class_prep(sender, **kwargs):
    print "Class prepared %s" % sender
    
class_prepared.connect(print_class_prep)

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

class AbstractSecureModelRoleMetaClass(ModelBase):
    '''Constructs the classes of all of SecurityRole's children'''
    
    class SecurityAttributeNameConflictError(Exception):
        '''Indicates that an attribute name was already used
        
        Attributes:
        @param attribute_name -- attribute name that caused the conflict
        @param msg -- optional explanation of the exception
        '''
        def __init__(self, attribute_name, msg=None):
            if msg == None:
                self.msg = "Attribute name %s already used by the Security application" % attribute_name
                
            self.attribute_name = attribute_name

    class RoleNameConflictError(Exception):
        '''Indicates that the role name was already used in another class
        
        Attributes:
        @param role_name -- role name that caused the conflict
        @param msg -- explanation of the exception
        '''
        def __init__(self, role_name, msg=None):
            self.role_name = role_name
            if msg == None:
                self.msg = "Role name %s already used in another Role class" % role_name
                
    class MisconfigurationError(Exception):
        '''Indicates that some misconfiguration has occurred'''
        pass

    def __new__(cls, name, bases, dict):
        '''Create an AbstractSecureModelRole class customized to the particular model'''
        
        print "Called %s.__new__ for %s" % (cls.__name__, name)
        print "Dict has:"
        for k,v in dict.iteritems():
            print "    %s: %s" % (k,v)
        
#        # Don't add anything for the abstract models
#        if name is not "AbstractSecureModelRole" or dict['__module__'] is not cls.__module__:
#            print "Adding special fields"
#            
#            model_name = None
#            # Check if modelname was given directly
#            if 'model_name' in dict:
#                model_name = dict['model_name']
#            
#            # Otherwise check in the base classes
#            else:
#                for b in bases:
#                    if hasattr(b, 'model_name'): model_name = b.model_name
#                    break
#            
#            if not model_name:
#                raise cls.MisconfigurationError("Could not find model_name attribute for new class %s.%s" % (dict['__module__'], name)
        
#        # add choices for roles
#        classes = cls._get_all_role_classes(dict)
#        
#        choices = []
#        role_mappings = dict()
#        for klass_name, klass in classes.iteritems():
#            # default role name to the name of the class
#            role_name = getattr(klass, 'role_name', klass_name)
#            # make sure that the choices are unique
#            if role_name in role_mappings:
#                raise cls.RoleNameConflictError(role_name)
#            
#            choices.append(role_name, klass.role_desc)
#            role_mappings[role_name] = klass
#        
#        # add a choice field for the class
#        dict['security_role_choice'] = models.CharField(max_length=200, choices=choices)
#        dict['role_mappings'] = role_mappings
        
        # Create the class
        cls = super(AbstractSecureModelRoleMetaClass, cls).__new__(cls, name, bases, dict)
        
#        _connect_role_signals(cls)
        return cls
    
    @classmethod
    def _get_all_role_classes(cls, dict):
        '''Gets all the defined inner classes that inherit from SecurityRole.Role'''
        
        return dict([(k,v) for (k,v) in dict.iteritems() if isinstance(v, ClassType) and issubclass(v, AbstractSecureModelRole.Role)])
    
class AbstractSecureModelRole(models.Model):
    '''
    Defines the relationship of every object to every user.
    By default, not all users can see/modify all SecureModel objects.
    '''
    
    is_restrictive = models.BooleanField('Does this role further restrict or provide additional permissions?')
        
    __metaclass__ = AbstractSecureModelRoleMetaClass
    
    class Meta:
        abstract = True
    
    def __unicode__(self):
        return "Role: %s, user: %s, object: %s" % (self.__class__,
                                                   self.security_user,
                                                   self.security_object)

    class Role(object):
        '''Abstract role. Defines the dynamic permissions on objects.'''
    
        @classmethod
        def get_write_protected_fields(cls, user, new_obj, old_obj):
            '''
            compare the old and current copies of the object
            and return a list of the field names that should not be allowed
            to be written or whose modifications are not allowed by the user.
            
            Parameters:
            @param user       -- the user making the request
            @param new_obj    -- the modified object
            @param old_obj    -- the object currently in the database unmodified
                
            Return:
            @return list of disallowed fields
            '''
            raise NotImplementedError
        
        @classmethod
        def get_read_protected_fields(cls, user, obj):
            '''
            Return a list of the fields that the user is not allowed to see.
            Note that if the values for read-protected fields are modified, a
            SecurityException will be raised.
    
            Parameters:
            @param user      -- the user making the request
            @param obj       -- the object being read

            Return:
            @return list of secret fields
            '''
            raise NotImplementedError
            
        @classmethod
        def can_delete(cls, user, obj):
            '''
            Does this role allow user to delete the object?
    
            Parameters:
            @param user      -- the user making the request
            @param obj       -- the object being deleted

            Return:
            @return True if allowed False otherwise.
            '''
            raise NotImplementedError
        
        @classmethod
        def can_write(cls, user, obj):
            '''
            Does this role allow user to write the object?
    
            Parameters:
            @param user      -- the user making the request
            @param obj       -- the object being written

            Return:
            @return True if allowed False otherwise.
            '''
            raise NotImplementedError
            
        @classmethod
        def can_add_role(cls, req_user, obj, role, rcv_user):
            '''
            Does this role allow user 'req_user' to give the Role 'role'
            for object 'obj' to user 'rcv_user'?
    
            Parameters:
            @param req_user   -- The user making the request
            @param obj        -- The object over which the role is given
            @param role       -- The Role that is being given
            @param rcv_user   -- The user who will be given the new role
    
            Return:
            @return True if allowed False otherwise.
            '''
            raise NotImplementedError
        
        @classmethod
        def can_del_role(cls, req_user, obj, role, rcv_user):
            '''
            Does this role allow user 'req_user' to remove the SecurityRole.Role 'role'
            for object 'obj' from user 'rcv_user'?
    
            Parameters:
            @param req_user   -- The user making the request
            @param obj        -- The object over which the role is removed
            @param role       -- The SecurityRole.Role that is being removed
            @param rcv_user   -- The user from whome the role will be removed
    
            Return:
            @return True if allowed False otherwise.
            '''
            raise NotImplementedError
        
    class Owner(Role):
        '''Default role assigned to the owner of a newly created object'''
    
        @classmethod
        def get_write_protected_fields(cls, user, new_obj, old_obj):
            return []
        
        @classmethod
        def get_read_protected_fields(cls, user, obj):
            return []
        
        @classmethod
        def can_delete(cls, user, obj):
            return True
        
        @classmethod
        def can_write(cls, user, obj):
            return True
                    
        @classmethod
        def can_add_role(cls, req_user, obj, role, rcv_user):
            return True
        
        @classmethod
        def can_del_role(cls, req_user, obj, role, rcv_user):
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

class SecureModelMetaClass(ModelBase):
    def __new__(cls, name, bases, dict):
        import sys
        
        print "Called SecureModelMetaClass.__new__ for %s" % name
        
        # Don't do anything special for the abstract class
        if name is not 'AbstractSecureModel' or dict['__module__'] is not cls.__module__:
            print "Adding special fields"
            # First create a new class for the securityroles for this model
            __import__(dict['__module__'])
            module = sys.modules[dict['__module__']]
            role_class = cls.create_abstractrole_class(name, module)
#            abstract_role_name = "%s.%s" % (role_class.__module__, role_class.__name__)
            abstract_role_name = "%s" % role_class.__name__
    
            # Check if the Model is a child of another model that already
            # has been processed and has security_object_users defined
            processed = False
            for base in bases:
                if issubclass(base, AbstractSecureModel) and base is not AbstractSecureModel:
                    processed = True
            
            if not processed:
                # Add the m2m field on the model
                dict['security_object_users'] = models.ManyToManyField(auth.models.User,
                                                                       through=abstract_role_name)

        # Create the Model class itself
        cls = super(SecureModelMetaClass, cls).__new__(cls, name, bases, dict)
        
        # Connect the signals to monitor changes to the instances
#        _connect_obj_signals(cls)
        return cls
    
    @classmethod
    def create_abstractrole_class(cls, model_name, module):
        role_name = "Abstract%sRole" % model_name
        related_name = "%ss" % model_name.lower()
        new_class = type(role_name,
                         (AbstractSecureModelRole,),
                         {'security_object': models.ForeignKey(model_name, related_name=related_name),
                          'security_user': models.ForeignKey(auth.models.User, related_name=related_name),
                          '__module__': module.__name__})
        setattr(module, new_class.__name__, new_class)
        return new_class
    
class AbstractSecureModel(models.Model):
    '''
    Define the default Manager in an abstract class so that
    it gets inherited in all successors in the inheritance hierarchy
    as defined by Django's Manage inheritance rules.

    All models that want to use the advanced permissions
    from the security app need to inherit from SecureModel.
    '''
    objects = SecureModelManager()

    __metaclass__ = SecureModelMetaClass

    class Meta:
        abstract = True
    
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

# NOTES:
# Models should not be defined with unique columns that are secret. Otherwise,
# when adding a new instance, the values might not be unique.
#
# Need to make sure to set the correct current user for ownership or to remove
# the ownership after adding and set the right roles

# TODO: Solve the inheritance issue where looking up roles gives generic SecurityRole objects.
