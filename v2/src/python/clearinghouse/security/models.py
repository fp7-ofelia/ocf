from django.db import models
from django.contrib import auth
from django.db.models.base import ModelBase
from clearinghouse.security import checks

class RoleMetaClass(type):
    '''Metaclass for concrete children of AbstractSecureModelRole.AbstractRole.
    Adds information about the new roles into the choices in the model role class.
    '''
    
    class RoleNameConflictError(Exception):
        '''
        @summary Indicates that the role name was already used in another class
        
        @param role_name -- role name that caused the conflict
        @param model_name -- name of Model for which this role is being defined
        @param msg -- explanation of the exception
        '''
        def __init__(self, role_name, model_name, msg=None):
            self.role_name = role_name
            if msg == None:
                self.msg = "Role name %s already used in another Role " \
                             + "class for model %s" % (role_name, model_name)

    def __new__(cls, name, bases, attrs):
#        print "****Called %s.__new__ for %s" % (cls, name)
#        print cls.__module__
#        print "Dict has:"
#        for k,v in attrs.iteritems():
#            print "    %s: %s" % (k,v)
        
        # Create the class
        new_class = super(RoleMetaClass, cls).__new__(cls, name, bases, attrs)
        
        # Only do it for non-abstract non-base roles
        if hasattr(new_class, 'model_role_class'):
#            print "Adding info"
            # Add the info into role_choices and role_mappings
            if name in new_class.model_role_class.role_mappings:
                raise RoleMetaClass.RoleNameConflictError(
                    name, new_class.model_role_class.model_fqn)
            new_class.model_role_class.role_choices.append((name, new_class.__doc__))
            new_class.model_role_class.role_mappings[name] = new_class
        
        return new_class

class AbstractSecureModelRole(models.Model):
    '''
    Defines the relationship of every object to every user.
    By default, not all users can see/modify all SecureModel objects.
    '''
    
    class Meta:
        abstract = True
    
    def __unicode__(self):
        return "Role: %s, user: %s, object: %s" % (self.__class__,
                                                   self.security_user,
                                                   self.security_object)
        
    @classmethod
    def get_roles_for_user(cls, user):
        roles = cls.objects.filter(security_user=user)
        for r in roles.all():
            r = r.role_mappings[r.security_role_choice]
            yield r
            
    def get_role(self):
        return self.role_mappings[self.security_role_choice]
    
    class BaseAbstractRole(object):
        '''@summary: Defines base permissions.'''
        
        __metaclass__ = RoleMetaClass
    
        @classmethod
        def get_write_protected_fields(cls, new_obj, old_obj):
            '''
            @summary: compare the old and current copies of the object
            and return a list of the field names that should not be allowed
            to be written or whose modifications are not allowed.
            
            @param new_obj    -- the modified object
            @param old_obj    -- the object currently in the database unmodified
                
            @return list of disallowed fields
            '''
            raise NotImplementedError
        
        @classmethod
        def get_read_protected_fields(cls, obj):
            '''
            @summary: Return a list of the fields that the user is not allowed to see.
            Note that if the values for read-protected fields are modified, a
            SecurityException will be raised.
    
            @param obj       -- the object being read
    
            @return list of secret fields
            '''
            raise NotImplementedError
            
        @classmethod
        def can_delete(cls, obj):
            '''
            @summary: Does this role allow deleting the object?
    
            @param obj       -- the object being deleted
    
            @return True if allowed False otherwise.
            '''
            raise NotImplementedError
        
        @classmethod
        def can_write(cls, obj):
            '''
            @summary: Does this role allow writing the object?
    
            @param obj       -- the object being written
    
            @return True if allowed False otherwise.
            '''
            raise NotImplementedError
            
        @classmethod
        def can_add_role(cls, obj, role, user):
            '''
            @summary: Does this role allow giving the Role 'role'
            for object 'obj' to user 'user'?
    
            @param obj        -- The object over which the role is given
            @param role       -- The Role class that is being given
            @param user       -- The user who will be given the new role
    
            @return True if allowed False otherwise.
            '''
            raise NotImplementedError
        
        @classmethod
        def can_del_role(cls, obj, role, user):
            '''
            @summary: Does this role allow removing the SecurityRole.Role 'role'
            for object 'obj' from user 'user'?
    
            @param obj        -- The object over which the role is removed
            @param role       -- The SecurityRole.Role class that is being removed
            @param user       -- The user from whom the role will be removed
    
            @return True if allowed False otherwise.
            '''
            raise NotImplementedError
            
    class BaseOwner(BaseAbstractRole):
        '''Gives full permissions.'''
    
        @classmethod
        def get_write_protected_fields(cls, new_obj, old_obj):
            return []
        
        @classmethod
        def get_read_protected_fields(cls, obj):
            return []
        
        @classmethod
        def can_delete(cls, obj):
            return True
        
        @classmethod
        def can_write(cls, obj):
            return True
                    
        @classmethod
        def can_add_role(cls, obj, role, user):
            return True
        
        @classmethod
        def can_del_role(cls, obj, role, user):
            return True

################################################################################
# Now the SecureModel Code
#
        
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

class SecureModelMetaClass(ModelBase):
    def __new__(cls, name, bases, dict):
        import sys
        
#        print "Called SecureModelMetaClass.__new__ for %s" % name
        
        # Don't do anything special for the abstract class
        if name is not 'AbstractSecureModel' or dict['__module__'] is not cls.__module__:
#            print "Adding special fields"
            # First create a new class for the securityroles for this model
            __import__(dict['__module__'])
            module = sys.modules[dict['__module__']]
            role_class = cls.create_baserole_class(name, module)
            base_role_name = "%s" % role_class.__name__
    
            # Add the m2m field on the model
            security_related_users_name = 'security_%s_users' % name.lower()
            dict[security_related_users_name] = \
                models.ManyToManyField(auth.models.User,
                                       through=base_role_name,
                                       related_name='security_%s_objects' % name.lower())
            dict['security_base_role_class'] = role_class

        # Create the Model class itself
        cls = super(SecureModelMetaClass, cls).__new__(cls, name, bases, dict)
        
        # Connect the signals to monitor changes to the instances
        checks._connect_obj_signals(cls)
        return cls
    
    @classmethod
    def create_baserole_class(cls, model_name, module):
        role_name = "Base%sRole" % model_name
        related_name = "security_%s_roles" % model_name.lower()
        
        # Create a new inner abstract_role specific to the model so we
        # can add an attribute to it pointing back to the outer class
        abstract_role_class = type('AbstractRole',
                                   (AbstractSecureModelRole.BaseAbstractRole,),
                                   {'__module__': module,
                                    '__metaclass__': RoleMetaClass})
        
        # Create the base role class
        role_choices = []
        new_class = type(role_name,
                         (AbstractSecureModelRole,),
                         {'security_object': models.ForeignKey(model_name, related_name=related_name),
                          'security_user': models.ForeignKey(auth.models.User, related_name=related_name),
                          'security_related_name': related_name,
                          'AbstractRole': abstract_role_class,
                          'role_choices': role_choices,
                          'role_mappings': {},
                          'model_fqn': "%s.%s" % (module.__name__, model_name),
                          'security_role_choice': models.CharField(max_length=200,
                                                                   choices=role_choices),
                          '__module__': module.__name__})
        
        # Add a pointer to new class so we can get role_choices and role_mappings
        abstract_role_class.model_role_class = new_class
        
        # Create and add the owner class
        owner_dict = AbstractSecureModelRole.BaseOwner.__dict__.copy()
        owner_dict['__module__'] = module
        new_class.Owner = type('Owner', (abstract_role_class,), owner_dict)
        
        # Add the new class to the list of loaded classes
        setattr(module, new_class.__name__, new_class)
        
        # Connect role signals so that changes to the role get checked
        checks.connect_role_signals(new_class)
        
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
        '''@summary: Exceptions caused by the security app for this model
        
        @param user -- user who caused the exception
        @param msg -- explanation of the exception
        '''
        def __init__(self, user, msg):
            self.user = user
            self.msg = msg
    
# TODO: NOTES:
# Models should not be defined with unique columns that are secret. Otherwise,
# when adding a new instance, the values might not be unique.
#
# Need to make sure to set the correct current user for ownership or to remove
# the ownership after adding and set the right roles
#
# Be careful with inheritance. A child's roles are different from the parent's.
# So if accessing an object using the parent, only the parent's roles are checked.