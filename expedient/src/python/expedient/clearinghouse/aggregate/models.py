'''
@author: jnaous
'''

import logging
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.contenttypes.models import ContentType
from expedient.common.extendable.models import Extendable
from expedient.common.permissions.shortcuts import \
    give_permission_to, delete_permission, must_have_permission, has_permission,\
    get_permittee_from_threadlocals
from expedient.common.permissions.models import Permittee
from expedient.common.permissions.utils import permissions_save_override,\
    permissions_delete_override
from expedient.common.permissions.decorators import require_obj_permissions_for_method
from expedient.common.permissions.exceptions import PermissionDenied

logger = logging.getLogger("aggregate.models")

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
    @ivar slice_set: A read-only property that returns a queryset of
        all slices allowed to use the aggregate (i.e. have the
        "can_use_aggregate" permission for this aggregate).
    @type slice_set: C{QuerySet} of C{Slice}s.
    @ivar managers: A read-only property that returns a queryset of
        all user allowed to edit the aggregate (i.e. have the
        "can_edit_aggregate" permission for this aggregate).
    @type managers: C{QuerySet} of C{User}s.
    '''
    
    information = \
"""
No information available.
"""
    
    update_caption = u"update"
    
    name = models.CharField(
        max_length=200, unique=True,
        help_text="Use a unique name for this aggregate.")
    logo = models.ImageField(
        'Logo', upload_to=settings.AGGREGATE_LOGOS_DIR,
        editable=False, blank=True, null=True,
        help_text="Select an optional logo.")
    description = models.TextField(default="")
    location = models.CharField(
        "Geographic Location", max_length=200, default="",
        help_text="AMs within the same island must "
        " share the exact same location.")
    available = models.BooleanField(
        "Available", default=True,
        help_text="Do you want to make this\
 aggregate available for others to use?")
    
    class Meta:
        verbose_name = "Generic Aggregate"

    save = permissions_save_override(
        permittee_kw="user",
        model_func=lambda: Aggregate,
        create_perm="can_add_aggregate",
        edit_perm="can_edit_aggregate",
        delete_perm="can_edit_aggregate",
    )
    delete = permissions_delete_override(
        permittee_kw="user",
        model_func=lambda: Aggregate,
        delete_perm="can_edit_aggregate",
    )
    
    def __unicode__(self):
        return u'Aggregate %s' % self.name
    
    def _get_managers(self):
        """Gets the list of users who have the "can_edit_aggregate" permission
        for this aggregate as a C{QuerySet} of C{User} objects.
        """
        return Permittee.objects.filter_for_class_and_permission_name(
            klass=User,
            permission="can_edit_aggregate",
            target_obj_or_class=self,
        )
    managers = property(_get_managers)
    
    def _get_slice_set(self):
        """Gets the list of slices allowed to use the aggregate"""
        from expedient.clearinghouse.slice.models import Slice
        return Permittee.objects.filter_for_class_and_permission_name(
            klass=Slice,
            permission="can_use_aggregate",
            target_obj_or_class=self,
        )
    slice_set = property(_get_slice_set)
        
        
    def check_status(self):
        """Checks whether the aggregate is available or not.
        
        @return: True if the aggregate is available, False otherwise.
        """
        return self.available
    
    def get_logo_url(self):
        try:
            return self.logo.url
        except Exception as e:
            #logger.debug("Exception getting logo url %s" % e)
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
                           kwargs={'agg_id': self.id})+"?next=%s" % next
        except NoReverseMatch:
            return reverse("aggregate_delete",
                           kwargs={'agg_id': self.id})+"?next=%s" % next

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
            
            give_permission_to("can_use_aggregate", self.as_leaf_class(), project)
        
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
        
        logger.debug("adding aggregate to project")
        
        must_have_permission("user", self.as_leaf_class(), "can_use_aggregate")
        
        prefix = self.__class__.get_url_name_prefix()
        try:
            return reverse("%s_aggregate_project_add" % prefix,
                           kwargs={'agg_id': self.id,
                                   'proj_id': project.id})+"?next=%s" % next
        except NoReverseMatch:
            logger.debug("Giving permission to use aggregate to %s" % project)
            give_permission_to("can_use_aggregate", self.as_leaf_class(), project)
            return next
        
    def remove_from_project(self, project, next):
        """
        Similar to L{add_to_project} but does the reverse, deleting the
        permission from the project using::
        
            from expedient.common.permissions.shortcuts import \
                delete_permission
                
            delete_permission("can_use_aggregate", self.as_leaf_class(), project)
            
        and then redirecting to C{next}. Additionally, if not overridden,
        this function stops all slices in the project before removing the
        aggregate. Subclasses should also stop slices.
        """
        must_have_permission("user", self.as_leaf_class(), "can_use_aggregate")
        
        prefix = self.__class__.get_url_name_prefix()
        try:
            return reverse("%s_aggregate_project_remove" % prefix,
                           kwargs={'agg_id': self.id,
                                   'proj_id': project.id})+"?next=%s" % next
        except NoReverseMatch:
            # Stop all the slices in the project for this aggregate.
            for slice in project.slice_set.all():
                try:
                    self.as_leaf_class().stop_slice(slice)
                except:
                    pass
                # Carolina: remove permision for aggregate in every slice inside the project
                self.remove_from_slice(slice, next)
            delete_permission("can_use_aggregate", self.as_leaf_class(), project)
            return next
        
    def add_to_slice(self, slice, next):
        """
        Works exactly the same as L{add_to_project} but for a slice.
        """
        must_have_permission("user", self.as_leaf_class(), "can_use_aggregate")
        must_have_permission("project", self.as_leaf_class(), "can_use_aggregate")
        
        prefix = self.__class__.get_url_name_prefix()
        try:
            return reverse("%s_aggregate_slice_add" % prefix,
                           kwargs={'agg_id': self.id,
                                   'slice_id': slice.id})+"?next=%s" % next
        except NoReverseMatch:
            give_permission_to("can_use_aggregate", self.as_leaf_class(), slice)
            return next

    def add_controller_to_slice(self, slice, next):
        """
        Works exactly the same as L{add_to_project} but for a slice.
        """
        must_have_permission("user", self.as_leaf_class(), "can_use_aggregate")
        must_have_permission("project", self.as_leaf_class(), "can_use_aggregate")

        prefix = self.__class__.get_url_name_prefix()
        try:
            return reverse("%s_aggregate_slice_controller_add" % prefix,
                           kwargs={'agg_id': self.id,
                                   'slice_id': slice.id})+"?next=%s" % next
        except NoReverseMatch:
            give_permission_to("can_use_aggregate", self.as_leaf_class(), slice)
            return next


    def remove_from_slice(self, slice, next):
        """
        Works exactly the same as L{remove_from_project} but for a slice.
        It stops the slice if not overridden. Subclasses should stop the
        slice before removing the permission.
        """
        must_have_permission("user", self.as_leaf_class(), "can_use_aggregate")
        must_have_permission("project", self.as_leaf_class(), "can_use_aggregate")

        prefix = self.__class__.get_url_name_prefix()
        try:
            return reverse("%s_aggregate_slice_remove" % prefix,
                           kwargs={'agg_id': self.id,
                                   'slice_id': slice.id})+"?next=%s" % next
        except NoReverseMatch:
            try:
                self.as_leaf_class().stop_slice(slice)
            except:
                pass
            delete_permission("can_use_aggregate", self.as_leaf_class(), slice)
            return next

    def add_to_user(self, user, next):
        """
        Works exactly the same as L{add_to_project} but for a user.
        """
        prefix = self.__class__.get_url_name_prefix()
        try:
            return reverse("%s_aggregate_user_add" % prefix,
                           kwargs={'agg_id': self.id,
                                   'user_id': user.id})+"?next=%s" % next
        except NoReverseMatch:
            give_permission_to("can_use_aggregate", self.as_leaf_class(), user)
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
                                   'user_id': user.id})+"?next=%s" % next
        except NoReverseMatch:
            delete_permission("can_use_aggregate", self.as_leaf_class(), user)
            return next

    def start_slice(self, slice):
        """Start the slice in the actual resources.
        
        Subclasses overriding this method should call the parent class
        to ensure permission checks.
        """
        must_have_permission("user", self.as_leaf_class(), "can_use_aggregate")
        must_have_permission("project", self.as_leaf_class(), "can_use_aggregate")
        must_have_permission("slice", self.as_leaf_class(), "can_use_aggregate")
        pass
    
    def stop_slice(self, slice):
        """Take out the resource reservation from the aggregates.

        Subclasses overriding this method should call the parent class
        to ensure permission checks.
        """
        user = get_permittee_from_threadlocals("user")
        can_use = has_permission(
            user, self.as_leaf_class(), "can_use_aggregate")
        can_edit = has_permission(
            user, self.as_leaf_class(), "can_edit_aggregate")
        if not can_use and not can_edit:
            raise PermissionDenied(
                "can_use_aggregate",
                self.as_leaf_class(),
                user, allow_redirect=False)
        pass
    
