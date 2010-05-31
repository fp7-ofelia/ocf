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
        except:
            return ""
        
    def get_edit_url(self):
        ct = ContentType.objects.get_for_model(self.__class__)
        print "get edit url for agg from app %s" % ct.app_label
        print reverse("%s_aggregate_edit" % ct.app_label,
                       kwargs={'agg_id': self.id})
        return reverse("%s_aggregate_edit" % ct.app_label,
                       kwargs={'agg_id': self.id})

    def get_aggregates_url(self):
        ct = ContentType.objects.get_for_model(self.__class__)
        return reverse("%s_aggregate_home" % ct.app_label,
                       kwargs={'agg_id': self.id})


    @classmethod
    def get_create_url(cls):
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
    
