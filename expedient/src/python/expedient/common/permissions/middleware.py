'''
Created on Jun 6, 2010

@author: jnaous
'''
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from models import Permittee, ExpedientPermission
from exceptions import PermissionDenied
import logging

logger = logging.getLogger("permissions.middleware")

class PermissionMiddleware(object):
    """
    Middleware to catch PermissionDenied exceptions thrown by the
    L{expedient.common.permissions} app and redirects to the permission URL
    if found. Also checks views and URLs for permission exceptions.
    """
    
    __views = {}
    __urls = {}

    def process_exception(self, request, exception):
        """
        Redirect to the denied permission's URL if it exists.
        """
        if type(exception) == PermissionDenied and exception.allow_redirect:
            target_type = ContentType.objects.get_for_model(exception.target)
            target = exception.target
            
            # Make sure there's a view for the permission before redirecting
            view = ExpedientPermission.objects.filter(
                name=exception.perm_name).values_list("view", flat=True)
            if not view[0]:
                return False
            
            if isinstance(exception.permittee, Permittee):
                permittee = exception.permittee.object
            else:
                permittee = exception.permittee
            permittee_type = ContentType.objects.get_for_model(permittee)

            url = reverse("permissions_url",
                kwargs={
                    "perm_name": exception.perm_name,
                    "target_ct_id": target_type.id,
                    "target_id": target.id,
                    "permittee_ct_id": permittee_type.id,
                    "permittee_id": permittee.id,
                },
            )
            
            # add a "from" key to the session for redirection after
            # permission is obtained for example.
            request.session["from_url"] = request.path
            request.session["from_method"] = request.method
            
            logger.debug("Got permission denied. Redirecting to %s" % url)
            
            return HttpResponseRedirect(url)
        
        return None
        
    @classmethod
    def add_required_url_permissions(cls, url, perm_names,
                                     permittee_func, target_func,
                                     methods=["GET", "POST"]):
        """
        Similar to the decorator L{decorators.require_objs_permissions_for_view} but
        not a decorator. Instead, this function protects a URL instead of the view
        function itself. The URL cannot be a regular expression however.
        
        @param url: The url for which permissions are to be enforced.
        @type url: C{str}
        @param perm_names: a list of permission names that are required.
        @type perm_names: L{list} of L{str}
        @param permittee_func: a callable that accepts the url's view's arguments
            and returns a model instance not necessarily a L{Permittee}
            instance.
        @type permittee_func: callable
        @param target_func: a callable that accepts the url's view's arguments
            and returns a C{QuerySet} instance of targets.
        @type target_func: callable
        @keyword methods: list of methods for which the requirement applies.
            Default is ["GET", "POST"].
        @type methods: C{list} of C{str}
        """
        info = dict(perm_names=perm_names,
                    permittee_func=permittee_func,
                    target_func=target_func,
                    methods=methods)
        cls.__urls.setdefault(url, []).append(info)
        
    @classmethod
    def add_required_view_permissions(cls, view_func, perm_names,
                                      permittee_func, target_func,
                                      methods=["GET", "POST"]):
        """Add permission requirements to a view function.
        
        @param view_func: The view function to add permission requirements to.
        @type view_func: callable.
        @param perm_names: a list of permission names that are required.
        @type perm_names: L{list} of L{str}
        @param permittee_func: a callable that accepts the view's arguments
            and returns a model instance not necessarily a L{Permittee}
            instance.
        @type permittee_func: callable
        @param target_func: a callable that accepts the view's arguments
            and returns a C{QuerySet} instance of targets.
        @type target_func: callable
        @keyword methods: list of methods for which the requirement applies.
            Default is ["GET", "POST"].
        @type methods: C{list} of C{str}
        """
        info = dict(perm_names=perm_names,
                    permittee_func=permittee_func,
                    target_func=target_func,
                    methods=methods)
        cls.__views.setdefault(view_func, []).append(info)
        
    def _check_view_perms(self, perms_info, request, view_args, view_kwargs):
        """Check if the permissions information in C{perms_info} apply"""
        if request.method in perms_info["methods"]:
            permittee = perms_info["permittee_func"](request, *view_args, **view_kwargs)
            targets = perms_info["target_func"](request, *view_args,
                                                **view_kwargs)

            missing, target = ExpedientPermission.objects.get_missing(
                permittee, perms_info["perm_names"], targets)
                    
            if missing:
                exc = PermissionDenied(missing.name, target, permittee)
                logger.info("Permission Denied %s" % exc)
                raise exc

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Check if the URL is in the list of URLs to watch for, then
        check the permissions for that URL.
        """
        for pi in self.__urls.get(request.path, []) + \
        self.__views.get(view_func, []):
            try:
                self._check_view_perms(pi, request, view_args, view_kwargs)
            except PermissionDenied as exception:
                r = self.process_exception(request, exception)
                if r:
                    return r
                else:
                    return HttpResponseRedirect(
                        reverse(
                            "permissions_reraise",
                            kwargs=dict(
                                perm_name=exception.perm_name,
                                target_ct_id=ContentType.objects.get_for_model(
                                    exception.target).id,
                                target_id=exception.target.id,
                                permittee_ct_id=ContentType.objects.get_for_model(
                                    exception.permittee).id,
                                permittee_id=exception.permittee.id,
                            ),
                        )
                    )
        return None
    
