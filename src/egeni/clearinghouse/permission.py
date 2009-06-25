from egeni.clearinghouse import views, models
from django.http import HttpResponseForbidden

class CheckOwnership(object):
    """
    This middleware class will check that a user owns the slices and the
    flowspaces that are in the url he is using.
    """
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        '''Check if the user does not own the slice'''
        
        if 'slice_id' in view_kwargs:
            objs = models.Slice.objects.filter(id=view_kwargs['slice_id'])
            # if the object exists and user is not the owner
            if objs.count() and not objs.filter(owner=request.user).count():
                return HttpResponseForbidden()

        return None
