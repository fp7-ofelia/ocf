from django.db import models
from django.db.models.base import ModelBase
from django.contrib import auth
from django.db.models.fields import Field
from clearinghouse.middleware import threadlocals
from django.contrib.contenttypes.generic import GenericForeignKey
from django.db.models.signals import pre_save, post_save, post_init
from django.conf import settings, global_settings
import checks


class Category(models.Model):
    '''DIFC category'''
    
    __owners = models.ManyToManyField(auth.models.User,
                                      related_name="owned_categories")
    
    __users = models.ManyToManyField(auth.models.User,
                                    related_name="usable_categories")

    def add_owner(self, user):
        '''@summary: Check that the current user can give ownership
        
        @param user: user to give ownership to
        '''
        if threadlocals.get_current_user() in list(self.__owners.all()):
            self.__owners.add(user)
        else:
            raise checks.SecurityException(
                "User cannot give ownership to %s" % user)
        
    def disown(self):
        '''@summary remove current user from owners'''
        try:
            self.__owners.remove(threadlocals.get_current_user())
        except:
            pass
    
    def add_user(self, user):
        '''@summary: Check that current user is allowed to give usage and do it
        
        @param user: User to allow access
        '''
        if threadlocals.get_current_user() in list(self.__owners.all()):
            self.__users.add(user)
        else:
            raise checks.SecurityException(
                "User cannot give ownership to %s" % user)
            
    def remove_user(self, user):
        if threadlocals.get_current_user() in list(self.__owners.all()) or \
        user == threadlocals.get_current_user():
            try:
                self.__users.remove(user)
            except:
                pass
        else:
            raise checks.SecurityException(
                "User cannot deny use to %s" % user)
        
    def __unicode__(self):
        return u"%s" % self.id
    
    @classmethod
    def post_save(cls, sender, **kwargs):
        cat = kwargs['instance']
        if len(cat.__owners) == 0:
            cat.__owners.add(threadlocals.get_current_user())

post_save.connect(Category.post_save, Category)

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
    def get_secrecy_label_name(cls, attname):
        return "%s_secrecy_label" % attname
    
    @classmethod
    def get_integrity_label_name(cls, attname):
        return "%s_integrity_label" % attname
    
    @classmethod
    def get_catset_related_name(cls, modelname, attname, type):
        return "related_%s_%s_%s_objects" % (modelname, attname, type)

    def __new__(cls, name, bases, attrs):
        # for each field, add a difc label field
        for attname, att in attrs.items():
            if isinstance(att, Field):
                attrs[cls.get_secrecy_label_name(attname)] = \
                    models.ManyToManyField(
#                        CategorySet,
                        Category,
                        related_name=cls.get_catset_related_name(
                            name, attname, "secrecy"))
                attrs[cls.get_integrity_label_name(attname)] = \
                    models.ManyToManyField(
#                        CategorySet,
                        Category,
                        related_name=cls.get_catset_related_name(
                            name, attname, "integrity"))
        klass = super(SecureModelBase, cls).__new__(cls, name, bases, attrs)
        pre_save.connect(checks.check_object_save, klass)
        # store table-name for model in settings
        settings.secure_models = getattr(settings, "secure_models", [])
        settings.secure_models.append(klass._meta.db_table)
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
    
    def __init__(self, *args, **kwargs):
        super(SecureModel, self).__init__(*args, **kwargs)
        # TODO: clear or hide? all fields that are not allowed to be seen

    def get_FIELD_label(self, attname):
        '''@summary: get a 2-tuple of secrecy and integrity categories for
        field 'attname'
        
        @param attname: Name of the field whose label we want
        '''
        
        secrecy_sets_name = self.__class__.__metaclass__.\
            get_secrecy_label_name(attname)
        integrity_sets_name = self.__class__.__metaclass__.\
            get_integrity_label_name(attname)
        
        s_catsets = getattr(self, secrecy_sets_name).all()
        i_catsets = getattr(self, integrity_sets_name).all()

        return (s_catsets, i_catsets)

    class Meta:
        abstract = True
