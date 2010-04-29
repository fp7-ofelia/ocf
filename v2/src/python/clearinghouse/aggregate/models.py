from django.db import models
from clearinghouse.extendable.models import Extendable
from clearinghouse.slice.models import Slice
from clearinghouse.project.models import Project
from django.contrib import auth
from django.conf import settings

class Aggregate(Extendable):
    '''
    Holds information about an aggregate. Needs to be extended by plugins.
    
    @param name: human-readable name of the Aggregate
    @type name: L{str}
    '''
    
    name = models.CharField(max_length=200, unique=True)
    logo = models.ImageField('Logo', upload_to=settings.AGGREGATE_LOGOS_DIR,
                             blank=True, null=True)
    type = 'Generic'
    description = models.TextField()
    location = models.CharField("Location", max_length=200)
    
    class Extend:
        fields = {
            'admins_info': (
                models.ManyToManyField,
                ("AggregateAdminInfo",),
                {"verbose_name": "Info about users allowed to administer the aggregate"},
                ("admin_info_class",),
                {'through': 'admin_info_through',
                 'verbose_name': "admins_comment",},
            ),
            'users_info': (
                models.ManyToManyField,
                ("AggregateUserInfo",),
                {"verbose_name": "Info about users allowed to use aggregate"},
                ("user_info_class",),
                {'through': 'user_info_through',
                 "verbose_name":  "users_comment"},
            ),
            'slices_info': (
                models.ManyToManyField,
                ("AggregateSliceInfo",),
                {"verbose_name":  "Info on slices using the aggregate"},
                ("slice_info_class",),
                {'through': 'slice_info_through',
                 'verbose_name': "slices_comment"},
            ),
            'projects_info': (
                models.ManyToManyField,
                ("AggregateProjectInfo",),
                {'verbose_name': "Info on projects using the aggregate"},
                ("project_info_class",),
                {'through': 'project_info_through',
                 'verbose_name':  "projects_comment"},
            ),
        }

    def create_slice(self, slice_id, *args, **kwargs):
        '''Create a new slice with the given slice_id
        and the resources specified. Does not actually
        make the reservation. Use start_slice for that.
        
        @param slice_id: unique id to give to the slice
        @type slice_id: L{str}
        @param args: additional optional arguments
        @param kwargs: additional optional keyword arguments
        '''
        raise NotImplementedError()
    
    def start_slice(self, slice_id, *args, **kwargs):
        '''Reserves/allocates the resources in the aggregate
        
        @param slice_id: unique id of slice to start
        @type slice_id: L{str}
        @param args: additional optional arguments
        @param kwargs: additional optional keyword arguments
        '''
        raise NotImplementedError()
    
    def delete_slice(self, slice_id, *args, **kwargs):
        '''Delete slice with given slice_id
        
        @param slice_id: unique id of slice to delete
        @type slice_id: L{str}
        @param args: additional optional arguments
        @param kwargs: additional optional keyword arguments
        '''
        raise NotImplementedError()
    
    def stop_slice(self, slice_id, *args, **kwargs):
        '''Stops running the slice, but does not delete it.
        
        @param slice_id: unique id of slice to stop
        @type slice_id: L{str}
        @param args: additional optional arguments
        @param kwargs: additional optional keyword arguments
        '''
        raise NotImplementedError()
    
    def get_logo_url(self):
        try:
            return self.logo.url
        except:
            return ""

class AggregateUserInfo(Extendable):
    '''
    Generic additional information about a user to use the aggregate.
    
    @param user: user to which this info relates
    @type user: One-to-one mapping to L{auth.models.User}
    @param aggregates: aggregates which the owner of this info can use
    @type aggregates: L{models.ManyToManyField} to L{Aggregate}
    '''

    class Extend:
        fields = {
            'aggregates': (
                models.ManyToManyField,
                (Aggregate,),
                {'verbose_name': "Aggregates the user is allowed to use"},
                ("aggregate_class",),
                {'through': 'aggregates_through',
                 'verbose_name': "aggregates_comment"},
            ),
            'user': (
                models.OneToOneField,
                (auth.models.User,),
                {"verbose_name": "User to which this info relates"},
                (None,),
                {"verbose_name":  "user_comment"},
            ),
        }
        
    class Meta:
        abstract = True

class AggregateAdminInfo(Extendable):
    
    class Extend:
        fields = {
            'aggregates': (
                models.ManyToManyField,
                (Aggregate,),
                {'verbose_name': "Aggregates the user is allowed to administer"},
                ("aggregate_class",),
                {'through': 'aggregates_through',
                 'verbose_name':  "aggregates_comment"},
            ),
            'user': (
                models.OneToOneField,
                (auth.models.User,),
                {"verbose_name":  "User to which this info relates"},
                (None,),
                {"vebose_name": "user_comment"},
            ),
        }
        
    class Meta:
        abstract = True
        
class AggregateSliceInfo(Extendable):
    
    class Extend:
        fields = {
            'aggregates': (
                models.ManyToManyField,
                (Aggregate,),
                {'verbose_name': "Aggregates the slice is allowed to use"},
                ("aggregate_class",),
                {'through': 'aggregates_through',
                 'verbose_name': "aggregates_comment"},
            ),
            'slice': (
                models.OneToOneField,
                (Slice,),
                {"verbose_name": "Slice to which this info relates"},
                (None,),
                {"verbose_name": "slice_comment"},
            ),
        }
        
    class Meta:
        abstract = True
        
class AggregateProjectInfo(Extendable):
    
    class Extend:
        fields = {
            'aggregates': (
                models.ManyToManyField,
                (Aggregate,),
                {'verbose_name': "Aggregates the project is allowed to use"},
                ("aggregate_class",),
                {'through': 'aggregates_through',
                 'verbose_name': "aggregates_comment"},
            ),
            'project': (
                models.OneToOneField,
                (Project,),
                {"verbose_name":  "Project to which this info relates"},
                (None,),
                {"verbose_name": "project_comment"},
            ),
        }
        
    class Meta:
        abstract = True
        
