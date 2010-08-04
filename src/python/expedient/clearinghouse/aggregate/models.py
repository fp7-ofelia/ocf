'''
@author jnaous
'''

import logging
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.contenttypes.models import ContentType
from expedient.common.extendable.models import Extendable
from expedient.common.permissions.shortcuts import must_have_permission,\
    give_permission_to, delete_permission
from expedient.common.middleware import threadlocals
from expedient.common.permissions.models import Permittee

logger = logging.getLogger("Aggregate Models")

class Aggregate(Extendable):
    '''
    Holds information about an aggregate. Needs to be extended by plugins.
    
    @cvar information: Information about the aggregate. Used when displaying
        information about the type. Should be overriden.
    
    @ivar name: human-readable name of the Aggregate
    @type name: L{str}
    @ivar logo: Logo for the aggregate (an uploaded file).
    @type logo: C{models.ImageField}
    @ivar description: Description of this aggregate
    @type description: Text Field
    @ivar location: The location of the aggregate.
    @type location: a string that is understandable by Google Maps.
    @ivar available: Is the aggregate available for use?
    @type available: C{bool}
    @ivar managers: A read-only property that returns a queryset of
        all user allowed to edit the aggregate (i.e. have the
        "can_edit_aggregate" for this aggregate).
    @type managers: C{QuerySet} of C{User}s.
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
    description = models.TextField(default="")
    location = models.CharField(
        "Geographic Location", max_length=200, default="")
    available = models.BooleanField(
        "Available", default=True,
        help_text="Do you want to make this\
 aggregate available for others to use?")
    
    class Meta:
        verbose_name = "Generic Aggregate"

    def save(self, *args, **kwargs):
        """
        Override the default save method to enforce permissions.
        """
        pk = getattr(self, "pk", None)
        if not pk:
            # it's a new instance being created
            must_have_permission("user", Aggregate, "can_add_aggregate")
        else:
            must_have_permission("user", self, "can_edit_aggregate")
            
        super(Aggregate, self).save(*args, **kwargs)
        
        if not pk:
            # it was just created so give creator edit permissions
            d = threadlocals.get_thread_locals()
            give_permission_to(
                "can_edit_aggregate", self, d["user"], can_delegate=True)
        
    def delete(self, *args, **kwargs):
        """
        Override the default delete method to enforce permissions.
        """
        must_have_permission("user", self, "can_edit_aggregate")
        super(Aggregate, self).delete(*args, **kwargs)
        
    def get_managers(self):
        """Gets the list of users who have the "can_edit_aggregate" permission
        for this aggregate.
        
        @return: a C{QuerySet} of C{User} objects.
        """
        return Permittee.objects.filter_for_class_and_permission_name(
            klass=User,
            permission="can_edit_aggregate",
            target_obj_or_class=self,
        )
    managers = property(get_managers)
        
    def check_status(self):
        """Checks whether the aggregate is available or not.
        
        @return: True if the aggregate is available, False otherwise.
        """
        return self.available
    
    def get_logo_url(self):
        try:
            return self.logo.url
        except Exception as e:
            logger.debug("Exception getting logo url %s" % e)
            return ""
        
    @classmethod
    def get_url_name_prefix(cls):
        """
        Get the prefix to append to the beginning of url names when
        getting default urls.
        
        By default this returns the application name.
        """
        ct = ContentType.objects.get_for_model(cls)
        return ct.app_label
        
    def get_edit_url(self):
        """Get the url of where to go to edit the aggregate"""
        return reverse(
            "%s_aggregate_edit" % self.__class__.get_url_name_prefix(),
            kwargs={'agg_id': self.id})
        
    def get_delete_url(self, next):
        """
        Get the URL to use when deleting the project from the
        Aggregate List. This function will first check if there is a URL
        defined as <app_label>_aggregate_delete and return that if it
        exists, attaching "?next=<C{next}>" to the end of the URL.
        
        @param next: URL to redirect to after deleting object.
        
        @return: URL to go to when requesting the aggregate be deleted.
        """
        prefix = self.__class__.get_url_name_prefix()
        try:
            return reverse("%s_aggregate_delete" % prefix,
                           kwargs={'agg_id': self.id})+"?next="+next
        except NoReverseMatch:
            return reverse("aggregate_delete",
                           kwargs={'agg_id': self.id})+"?next="+next

    @classmethod
    def get_aggregates_url(cls):
        """Get the URL for aggregates of this type"""
        ct = ContentType.objects.get_for_model(cls)
        return reverse("aggregate_info", args=[ct.id])

    @classmethod
    def get_create_url(cls):
        """Get the URL to create aggregates of this type"""
        prefix = cls.get_url_name_prefix()
        return reverse("%s_aggregate_create" % prefix)
    
    def add_to_project(self, project, next):
        """
        Gives the aggregate a chance to request additional information for a
        project. This method should return a URL to redirect to where the
        user can create or update the additional information the aggregate
        needs. When done, the view at that URL should use the
        C{give_permission} function to give the project
        the "can_use_aggregate" permission::
            
            from expedient.common.permissions.shortcuts import \
                give_permission_to
            
            give_permission_to("can_use_aggregate", self, project)
        
        and then it should redirect to C{next}.
        
        If no extra information is needed, this function can return C{next},
        instead of a custom URL, but it still needs to give the project the
        "can_use_aggregate" permission.
        
        Unless overridden in a subclass, this function will look for a url
        with name <app_name>_aggregate_project_add by reversing the name with
        it parameters 'agg_id' and 'proj_id'. It will append '?next=<next>' to
        the URL if found. Otherwise, it simply gives the permission to the
        project and returns C{next}.
        """
        prefix = self.__class__.get_url_name_prefix()
        try:
            return reverse("%s_aggregate_project_add" % prefix,
                           kwargs={'agg_id': self.id,
                                   'proj_id': project.id})+"?next="+next
        except NoReverseMatch:
            give_permission_to("can_use_aggregate", self, project)
            return next
        
    def remove_from_project(self, project, next):
        """
        Similar to L{add_to_project} but does the reverse, deleting the
        permission from the project using::
        
            from expedient.common.permissions.shortcuts import \
                delete_permission
                
            delete_permission("can_use_aggregate", self, project)
            
        and then redirecting to C{next}. Additionally, if not overridden,
        this function stops all slices in the project before removing the
        aggregate. Subclasses should also stop slices.
        """
        prefix = self.__class__.get_url_name_prefix()
        try:
            return reverse("%s_aggregate_project_remove" % prefix,
                           kwargs={'agg_id': self.id,
                                   'proj_id': project.id})+"?next="+next
        except NoReverseMatch:
            # Stop all the slices in the project for this aggregate.
            for slice in project.slice_set.all():
                try:
                    self.as_leaf_class().stop_slice(slice)
                except:
                    pass
            delete_permission("can_use_aggregate", self, project)
            return next
        
    def add_to_slice(self, slice, next):
        """
        Works exactly the same as L{add_to_project} but for a slice.
        """
        prefix = self.__class__.get_url_name_prefix()
        try:
            return reverse("%s_aggregate_slice_add" % prefix,
                           kwargs={'agg_id': self.id,
                                   'slice_id': slice.id})+"?next="+next
        except NoReverseMatch:
            give_permission_to("can_use_aggregate", self, slice)
            return next

    def remove_from_slice(self, slice, next):
        """
        Works exactly the same as L{remove_from_project} but for a slice.
        It stops the slice if not overridden. Subclasses should stop the
        slice before removing the permission.
        """
        prefix = self.__class__.get_url_name_prefix()
        try:
            return reverse("%s_aggregate_slice_remove" % prefix,
                           kwargs={'agg_id': self.id,
                                   'slice_id': slice.id})+"?next="+next
        except NoReverseMatch:
            try:
                self.as_leaf_class().stop_slice(slice)
            except:
                pass
            delete_permission("can_use_aggregate", self, slice)
            return next

    def add_to_user(self, user, next):
        """
        Works exactly the same as L{add_to_project} but for a user.
        """
        prefix = self.__class__.get_url_name_prefix()
        try:
            return reverse("%s_aggregate_user_add" % prefix,
                           kwargs={'agg_id': self.id,
                                   'user_id': user.id})+"?next="+next
        except NoReverseMatch:
            give_permission_to("can_use_aggregate", self, user)
            return next

    def remove_from_user(self, user, next):
        """
        Works exactly the same as L{remove_from_project} but for a user.
        Does not stop any slices.
        """
        prefix = self.__class__.get_url_name_prefix()
        try:
            return reverse("%s_aggregate_user_remove" % prefix,
                           kwargs={'agg_id': self.id,
                                   'user_id': user.id})+"?next="+next
        except NoReverseMatch:
            delete_permission("can_use_aggregate", self, user)
            return next

    def start_slice(self, slice):
        """Start the slice in the actual resources."""
        raise NotImplementedError()
    
    def stop_slice(self, slice):
        """Take out the resource reservation from the aggregates."""
        raise NotImplementedError()
    