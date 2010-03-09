from django.db import models
from django.db.models.base import ModelBase
from django.contrib import auth
from django.db.models.fields import Field
from clearinghouse.middleware import threadlocals

class SecureModelManager(models.Manager):
    '''
    Default Manager class for SecureModel subclasses. Mainly used
    to restrict the returned QuerySet
    '''

    use_for_related_fields = True
    
    def get_query_set(self):
        '''
        Return a SecureQuerySet that filters objects.
        
        @return the SecureQuerySet instance
        '''
        from clearinghouse.difc.query import SecureQuerySet
        
        # the full query set
        return SecureQuerySet(self.model)

class SecureModelBase(ModelBase):
    '''Add DIFC labels to SecureModel sub-class fields'''
    
    @classmethod
    def get_label_name(cls, attname):
        return "%s_difc_label" % attname
    
    def __new__(cls, name, bases, attrs):
        # for each field, add a difc label field
        for attname, att in attrs.items():
            if isinstance(att, Field):
                attrs[cls.get_label_name(attname)] = \
                    models.ManyToManyField('Category')
        klass = super(SecureModelBase, cls).__new__(cls, name, bases, attrs)
        
        return klass

class SecureModel(models.Model):
    '''
    Define the default Manager in an abstract class so that
    it gets inherited in all successors in the inheritance hierarchy
    as defined by Django's Manage inheritance rules.

    All models that want to use the advanced permissions
    from the security app need to inherit from SecureModel.
    '''
    
    objects = SecureModelManager()
    
    __metaclass__ = SecureModelBase
    
    class Meta:
        abstract = True
    
class Category(models.Model):
    '''DIFC category'''
    
    __owners = models.ManyToManyField(auth.models.User,
                                    related_name="owned_categories")
    
    __users = models.ManyToManyField(auth.models.User,
                                   related_name="clearance_categories")
    
    def __init__(self, *args, **kwargs):
        super(models.Model, self).__init__(*args, **kwargs)
        
        if len(self.__owners.all()) == 0:
            self.__owners.add(threadlocals.get_current_user())
        
    def give_ownership_to(self, user):
        '''@summary: Check that the current user can give ownership
        
        @param user: user to give ownership to
        '''
        if threadlocals.get_current_user() in list(self.__owners.all()):
            self.__owners.add(user)
        else:
            raise Category.SecurityException(
                "User cannot give ownership to %s" % user)
        
    def disown(self):
        '''@summary remove current user from owners'''
        try:
            self.__owners.remove(threadlocals.get_current_user())
        except:
            pass
    
    def give_clearance_to(self, user):
        '''@summary: Check that the current user can give clearance
        
        @param user: user to give clearance to
        '''
        if threadlocals.get_current_user() in list(self.__owners.all()):
            self.__users.add(user)
        else:
            raise Category.SecurityException(
                "User cannot give clearance to %s" % user)
            
    def remove_clearance_from(self, user):
        '''@summary: Remove clearance from user 'user'
        
        @param user: user to remove clearance from.
        '''
        if threadlocals.get_current_user() in list(self.__owners.all()):
            self.__users.remove(user)
        else:
            raise Category.SecurityException(
                "User cannot remove clearance from %s" % user)

    class SecurityException(Exception):
        '''@summary: Exceptions caused by the difc app for this category
        
        @param user -- user who caused the exception
        @param msg -- explanation of the exception
        '''
        def __init__(self, user, msg):
            self.user = user
            self.msg = msg
