from django.db import models
from django.contrib import auth
from pyanno import abstractMethod, parameterTypes, returnType
from clearinghouse.middleware import threadlocals
from django.db.models.signals import pre_save

class SecureModelManager(models.Manager):
    '''
    Default Manager class for SecureModel subclasses. Mainly used
    to restrict the returned QuerySet
    '''
    
    use_for_related_fields = True
    
    def __init__(self, *args, **kwargs):
        # by default don't give users with unknown roles
        # any access to an object.
        self.protect_unknown_roles = True
    
    def get_query_set(self):
        '''
        Return a filtered QuerySet, with objects that are not allowed
        to be seen filtered out.
        
        @return the filtered QuerySet instance
        '''
        
        # the full query set
        all = super(SecureModelManager, self).get_query_set()
        
        print "as_sql:"
        print all.query.as_sql()
        print "where:"
        print all.query.where
        print "extra_where:"
        print all.query.extra_where
        print "select:"
        print all.query.select
        print "get_columns():"
        print all.query.get_columns()
        
        if not self.protect_roleless_objects:
            return all

        # get the user requesting the query set
        user = threadlocals.get_current_user()
        
        # Get the security_role_sets whose user is the current user
        # and that refer to the objects we care about.
        # NOTE: by default objects that are not related to the user through
        #       a SecurityRole instance won't be considered, so won't be seen. 
        all_ids = all.values_list('pk', flat=True)
        security_roles = SecurityRole.objects.filter(
            _user=user, _object__in=list(all_ids))
        # get all the objects that have a SecurityRole in security_roles
        obj_ids = security_roles.values_list('_object', flat=True)
        all = all.filter(pk__in=set(obj_ids))
        
        # TODO: need to filter out objects where the query was
        # based on a hidden field
        # First, get the field names that the query uses
        
        return all

class SecureModel(models.Model):
    '''
    All models that want to use the advanced permissions
    from the security app need to inherit from SecureModel.
    '''
    
    objects = SecureModelManager()
    _obj_users = models.ManyToManyField(auth.models.User,
                                        through='SecurityRole')
    
    class SecurityException(Exception):
        '''Exceptions caused by the security app for this model
        
        Attributes:
        @param user -- user who caused the exception
        @param msg -- explanation of the exception
        '''
        def __init__(self, user, msg):
            self.user = user
            self.msg = msg

class SecurityRole(models.Model):
    '''
    Defines the relationship of every object to every user.
    By default, not all users can see/modify all objects. Adding
    this relationship between
    '''
    
    _user = models.ForeignKey(auth.models.User, related_name='security_roles')
    _object = models.ForeignKey(SecureModel, related_name='security_roles')
    
    @abstractMethod
    @parameterTypes(SecureModel)
    @returnType(list)
    def get_write_protected_fields(self, old_object):
        '''
        compare the old and current (self._object) copies of the object
        and return a list of the field names that should not be allowed
        to be written or whose modifications are not allowed by the user.
        
        Attributes:
        @param old_object -- the object currently in the database unmodified
            
        Return:
        @return list of disallowed fields
        '''
        pass
    
    @abstractMethod
    @returnType(list)
    def get_read_protected_fields(self):
        '''
        Return a list of the fields that the user is not allowed to see.
        Note that if the values for read-protected fields are modified, a
        SecurityException will be raised.

        Return:
        @return list of secret fields
        '''
        pass
    
    @abstractMethod
    @returnType(bool)
    def can_add_role(self, user, role):
        '''
        Does this role allow its owner (self._user) to add the role 'role' to
        the user 'user'?

        Attributes:
        @param user -- the user to which a role is being given
        @param role -- the role which is to be given to user
            
        Return:
        @return True if allowed False otherwise.
        '''
        pass

def do_write_check(sender, **kwargs):
    '''
    Get the old copy of the object, and send it to the security role
    to ask if the current copy has any fields that are write-protected.
    '''
    
    curr_obj = kwargs['instance']
    
    # get the user
    user = threadlocals.get_current_user()
    
    # Otherwise, get the SecurityRoles associated with this object
    # and the current user
    roles = curr_obj.security_roles.filter(_user=user)
    
    # check if there are no roles, so we need to check protect_unknown_roles
    if len(roles) == 0 and not curr_obj.__class__.objects.protect_unknown_roles:
        return

    # get the old object from the db
    try:
        old_obj = SecureModel.get(pk=curr_obj.pk)
    except SecureModel.DoesNotExist, e:
        # The object is not in the database to begin with.
        print "Saving instance %s for the first time" % curr_obj
        print e
        return
    
    # now get what each role doesn't allow to write, and see if
    # the intersection is empty => write is allowed by union of roles
    disallowed_fields = set(curr_obj._meta.fields)
    for role in roles.all():
        disallowed_fields.intersection_update(
            set(role.get_write_protected_fields(old_obj)))
    
    if len(disallowed_fields) > 0:
        vals = [curr_obj.get_attr(f) for f in disallowed_fields]
        raise curr_obj.__class__.SecurityException(user, "Writing to fields %s"
                " with the values %s not allowed" % (disallowed_fields, vals))
    
pre_save.connect()