'''
@author jnaous
'''

from django.db import models
from expedient.common.extendable.models import Extendable
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.contenttypes.models import ContentType

import logging
logger = logging.getLogger("Aggregate Models")

class Aggregate(Extendable):
    '''
    Holds information about an aggregate. Needs to be extended by plugins.
    
    @param name: human-readable name of the Aggregate
    @type name: L{str}
    '''
    
    information = \
"""
No information available.
"""
    
    name = models.CharField(
        max_length=200, unique=True,
        help_text="Use a unique name for this aggregate.")
    logo = models.ImageField(
        'Logo', upload_to=settings.AGGREGATE_LOGOS_DIR,
        editable=False, blank=True, null=True,
        help_text="Select an optional logo.")
    description = models.TextField()
    location = models.CharField("Geographic Location", max_length=200)
    available = models.BooleanField(
        "Available", default=True,
        help_text="Do you want to make this\
 aggregate available for others to use?")
    owner = models.ForeignKey(User, related_name="owned_aggregate_set")
    managers = models.ManyToManyField(
        User, related_name="managed_aggregate_set", blank=True,
        help_text="Who else should administer this aggregate?")
    users = models.ManyToManyField(User, related_name="useable_aggregate_set")
    
    class Meta:
        verbose_name = "Generic Aggregate"

    def check_status(self):
        return self.available
    
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

    def add_to_project(self, project, next):
        """
        Gives the aggregate a chance to request additional information for a
        project. This method should return a URL to redirect to where the
        user can create or update the additional information the aggregate
        needs. When done, the aggregate should add itself to the project's
        aggregates and then redirect to C{next}.
        
        If no extra information is needed, this function can return C{next}, 
        but it still needs to add the aggregate to the project.
        
        Unless overridden in a subclass, this function will look for a url
        with name <app_name>_aggregate_project_add by reversing the name with
        it parameters 'agg_id' and 'proj_id'. It will append '?next=<next>' to
        the URL if found. Otherwise, it simply adds the aggregate to the
        project and returns C{next}.
        """
        ct = ContentType.objects.get_for_model(self.__class__)
        try:
            return reverse("%s_aggregate_project_add" % ct.app_label,
                           kwargs={'agg_id': self.id,
                                   'proj_id': project.id})+"?next="+next
        except NoReverseMatch:
            project.aggregates.add(self)
            return next
        
    def remove_from_project(self, project, next):
        """
        Similar to L{add_to_project} but does the reverse, removing the
        aggregate from the project.
        """
        ct = ContentType.objects.get_for_model(self.__class__)
        try:
            return reverse("%s_aggregate_project_remove" % ct.app_label,
                           kwargs={'agg_id': self.id,
                                   'proj_id': project.id})+"?next="+next
        except NoReverseMatch:
            project.aggregates.remove(self)
            return next
        
    def add_to_slice(self, slice, next):
        """
        Works exactly the same as L{add_to_project} but for a slice.
        """
        ct = ContentType.objects.get_for_model(self.__class__)
        try:
            return reverse("%s_aggregate_slice_add" % ct.app_label,
                           kwargs={'agg_id': self.id,
                                   'slice_id': slice.id})+"?next="+next
        except NoReverseMatch:
            slice.aggregates.add(self)
            return next

    def remove_from_slice(self, slice, next):
        """
        Similar to L{add_to_slice} but does the reverse, removing the
        aggregate from the slice.
        """
        ct = ContentType.objects.get_for_model(self.__class__)
        try:
            return reverse("%s_aggregate_slice_remove" % ct.app_label,
                           kwargs={'agg_id': self.id,
                                   'slice_id': slice.id})+"?next="+next
        except NoReverseMatch:
            slice.aggregates.remove(self)
            return next

    @classmethod
    def get_aggregates_url(cls):
        """Get the URL for aggregates of this type"""
        ct = ContentType.objects.get_for_model(cls)
        return reverse("aggregate_info", args=[ct.id])

    @classmethod
    def get_create_url(cls):
        """Get the URL to create aggregates of this type"""
        ct = ContentType.objects.get_for_model(cls)
        return reverse("%s_aggregate_create" % ct.app_label)
    
    def start_slice(self, slice):
        """Start the slice in the actual resources."""
        raise NotImplementedError()
    
    def stop_slice(self, slice):
        """Take out the resource reservation from the aggregates."""
        raise NotImplementedError()
    