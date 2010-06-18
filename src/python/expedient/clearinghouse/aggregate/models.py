'''
@author jnaous
'''

from django.db import models
from expedient.common.extendable.models import Extendable
from expedient.clearinghouse.slice.models import Slice
from expedient.clearinghouse.project.models import Project
from django.contrib import auth
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
#from django.db.models import signals
#from expedient.common.permissions.utils import require_objs_permissions_for_url,\
#    get_user_from_req, get_queryset_from_class, get_queryset,\
#    get_queryset_from_id, register_permission_for_obj_or_class

import logging
logger = logging.getLogger("Aggregate Models")

class Aggregate(Extendable):
    '''
    Holds information about an aggregate. Needs to be extended by plugins.
    
    @param name: human-readable name of the Aggregate
    @type name: L{str}
    '''
    
    name = models.CharField(max_length=200, unique=True)
    logo = models.ImageField('Logo', upload_to=settings.AGGREGATE_LOGOS_DIR,
                             blank=True, null=True)
    description = models.TextField()
    location = models.CharField("Geographic Location", max_length=200)
    available = models.BooleanField("Available", default=True)
    
    admins_info = models.ManyToManyField(
        "AggregateAdminInfo", verbose_name="Administrators")
    users_info = models.ManyToManyField(
        "AggregateUserInfo", verbose_name="Users")
    slices_info = models.ManyToManyField(
        "AggregateSliceInfo", verbose_name="Slices using the aggregate")
    projects_info = models.ManyToManyField(
        "AggregateProjectInfo", verbose_name="Projects using the aggregate")
        
    class Meta:
        verbose_name = "Generic Aggregate"

    def get_logo_url(self):
        try:
            return self.logo.url
        except Exception as e:
            logger.debug("Exception getting logo url %s" % e)
            return ""
        
    def get_edit_url(self):
        """Get the url of where to go to edit the aggregate"""
        ct = ContentType.objects.get_for_model(self.__class__)
        return reverse("%s_aggregate_edit" % ct.app_label,
                       kwargs={'agg_id': self.id})

    @classmethod
    def get_aggregates_url(cls):
        """Get the URL for aggregates of this type""" 
        ct = ContentType.objects.get_for_model(cls)
        return reverse("%s_aggregate_home" % ct.app_label)


    @classmethod
    def get_create_url(cls):
        """Get the URL to create aggregates of this type"""
        ct = ContentType.objects.get_for_model(cls)
        return reverse("%s_aggregate_create" % ct.app_label)
    
    def check_status(self):
        return self.available

class AggregateUserInfo(Extendable):
    '''
    Generic additional information about a user to use the aggregate.
    
    @param user: user to which this info relates
    @type user: One-to-one mapping to L{auth.models.User}
    '''
    user = models.ForeignKey(auth.models.User)

class AggregateAdminInfo(Extendable):
    
    admin = models.ForeignKey(
        auth.models.User, verbose_name="Administrator")
    
class AggregateSliceInfo(Extendable):
    
    slice = models.ForeignKey(Slice)

class AggregateProjectInfo(Extendable):
    
    project = models.ForeignKey(Project)
    
# TODO: Fix aggregate permission checking
#def add_required_perms(sender, **kwargs):
#    """
#    For each class that is a subclass of Aggregate, add create, edit, and delete
#    permissions.
#    """
#    def add_edit_permissions(sender, **kwargs):
#        if kwargs['created']:
#            instance = kwargs['instance']
#            require_objs_permissions_for_url(
#                instance.get_edit_url(), ["can_view_aggregate"],
#                get_user_from_req, get_queryset_from_id(sender, instance.id),
#                methods=["GET"])
#            require_objs_permissions_for_url(
#                sender.get_edit_url(), ["can_edit_aggregate"],
#                get_user_from_req, get_queryset_from_id(sender, instance.id),
#                methods=["POST"])
#    
#    if issubclass(sender, Aggregate):
#        register_permission_for_obj_or_class(sender, "can_add_aggregate")
#        # Hookup to the create url
#        require_objs_permissions_for_url(
#            sender.get_create_url(), ["can_add_aggregate"],
#            get_user_from_req, get_queryset_from_class(sender))
#        
#        # Add signal to protect the editing URL
#        signals.post_save.connect(add_edit_permissions, sender=sender)
#        
#signals.class_prepared.connect(add_required_perms)
