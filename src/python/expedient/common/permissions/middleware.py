'''
Created on Jun 6, 2010

@author: jnaous
'''
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from models import PermissionUser, ExpedientPermission
from exceptions import PermissionDenied

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
            if not view[0]: return False
            
            if isinstance(exception.user, PermissionUser):
                user = exception.user.user
            else:
                user = exception.user
            user_type = ContentType.objects.get_for_model(user)
            
            url = reverse("permissions_url",
                kwargs={
                    "perm_name": exception.perm_name,
                    "target_ct_id": target_type.id,
                    "target_id": target.id,
                    "user_ct_id": user_type.id,
                    "user_id": user.id,
                },
            )
            
            # add a "next" field for redirection after permission is obtained.
            url += "?next=%s" % request.path
            
            return HttpResponseRedirect(url)
        
        return None
        
    @classmethod
    def add_required_url_permissions(cls, url, perm_names,
                                     user_func, target_func,
                                     methods=["GET", "POST"]):
        """
        Similar to the decorator L{decorators.require_objs_permissions_for_view} but
        not a decorator. Instead, this function protects a URL instead of the view
        function itself. The URL cannot be a regular expression however.
        
        @param url: The url for which permissions are to be enforced.
        @type url: C{str}
        @param perm_names: a list of permission names that are required.
        @type perm_names: L{list} of L{str}
        @param user_func: a callable that accepts the url's view's arguments
            and returns a model instance not necessarily a L{PermissionUser}
            instance.
        @type user_func: callable
        @param target_func: a callable that accepts the url's view's arguments
            and returns a C{QuerySet} instance of targets.
        @type target_func: callable
        @keyword methods: list of methods for which the requirement applies.
            Default is ["GET", "POST"].
        @type methods: C{list} of C{str}
        """
        info = dict(perm_names=perm_names,
                    user_func=user_func,
                    target_func=target_func,
                    methods=methods)
        cls.__urls.setdefault(url, []).append(info)
        
    @classmethod
    def add_required_view_permissions(cls, view_func, perm_names,
                                      user_func, target_func,
                                      methods=["GET", "POST"]):
        """
        Add a view to check for required permissions.
        
        @param url: The url for which permissions are to be enforced.
        @type url: C{str}
        @param perm_names: a list of permission names that are required.
        @type perm_names: L{list} of L{str}
        @param user_func: a callable that accepts the view's arguments
            and returns a model instance not necessarily a L{PermissionUser}
            instance.
        @type user_func: callable
        @param target_func: a callable that accepts the view's arguments
            and returns a C{QuerySet} instance of targets.
        @type target_func: callable
        @keyword methods: list of methods for which the requirement applies.
            Default is ["GET", "POST"].
        @type methods: C{list} of C{str}
        """
        info = dict(perm_names=perm_names,
                    user_func=user_func,
                    target_func=target_func,
                    methods=methods)
        cls.__views.setdefault(view_func, []).append(info)
        
    def _check_view_perms(self, perms_info, request, view_args, view_kwargs):
        """Check if the permissions information in C{perms_info} apply"""
        if request.method in perms_info["methods"]:
            user = perms_info["user_func"](request, *view_args, **view_kwargs)
            targets = perms_info["target_func"](request, *view_args,
                                                **view_kwargs)

            missing, target = ExpedientPermission.objects.get_missing(
                user, perms_info["perm_names"], targets)
                    
            if missing:
                raise PermissionDenied(missing.name, target, user)

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
                            exception.perm_name,
                            ContentType.objects.get_for_model(
                                exception.target).id,
                            exception.target.id,
                            ContentType.objects.get_for_model(
                                exception.user).id,
                            exception.user.id,
                        )
                    )
        return None
    