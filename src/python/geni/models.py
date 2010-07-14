'''
Created on Jul 4, 2010

@author: jnaous
'''

from django.db import models
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.common.utils import certtransport
from django.conf import settings
import xmlrpclib
from expedient.clearinghouse.slice.models import Slice
from geni import management

class GENISliceInfo(models.Model):
    """
    Holds information about the slice that's relevant for the GENI API.
    
    @ivar slice: The slice to which this information belongs.
    @type slice: OneToOneField to L{Slice}.
    @ivar slice_urn: the slice's unique resource name. This will be
        automatically created in the __init__ function if not given.
    @type slice_urn: a string.
    """
    slice = models.OneToOneField(
        Slice, related_name="geni_slice_info")
    slice_urn = models.CharField(max_length=1024)
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("slice_urn", management.create_slice_urn())
        super(GENISliceInfo, self).__init__(*args, **kwargs)
        
class GENIAggregate(Aggregate):
    url = models.URLField(max_length=200)
    
    class URLNotDefined(Exception): pass
    
    def __getattr__(self, name):
        if name == "proxy":
            try:
                u = self.url
            except AttributeError:
                raise self.URLNotDefined("URL not set.")
            
            if not u:
                raise self.URLNotDefined("URL not set.")
            
            transp = certtransport.SafeTransportWithCert(
                keyfile=settings.GCF_X509_CH_KEY,
                certfile=settings.GCF_X509_CH_CERT)
    
            self.proxy = xmlrpclib.ServerProxy(u, transport=transp)
    
    @classmethod
    def get_am_cred(cls):
        """
        Get the slice authority credentials to use for AM calls.
        
        @return: GENI credential string.
        """
        if hasattr(self, "am_cred"):
            return  cls.am_cred
        
        f = open(settings.GCF_NULL_SLICE_CRED)
        cls.am_cred = f.read()
        f.close()
        return cls.am_cred
    
    def _to_rspec(self, slice):
        """
        Change this slice into an rspec for this aggregates
        """
        raise NotImplementedError()
    
    def _list_resources(self):
        """
        Parse the rspec and update resources in the database.
        """
        raise NotImplementedError()
    
    def _create_sliver(self, slice):
        """
        Corresponds to the CreateSliver call of the GENI aggregate API.
        Creates a sliver on the aggregate from this slice.
        """
        
        rspec = self.as_leaf_class().to_rspec(slice)
        info = slice.geni_slice_info
        
        try:
            reserved = self.proxy.CreateSliver(
                info.slice_urn, [self.get_am_cred()], rspec)
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise Exception("Error creating sliver: %s" % e)
    
        # TODO: parse reserved slice to see errors and such
    
    def _delete_sliver(self, slice):
        """
        Corresponds to the DeleteSliver call of the GENI aggregate API.
        Stop and delete slice at the aggregate.
        """
        
        rspec = self.as_leaf_class().to_rspec(slice)
        info = slice.geni_slice_info
        
        try:
            ret = self.proxy.DeleteSliver(
                info.slice_urn, [self.get_am_cred()], rspec)
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise Exception("Error deleting sliver: %s" % e)
    
        return ret
        
    def sliver_status(self, slice):
        """
        Corresponds to the SliverStatus call of the GENI aggregate API.
        Returns the sliver's status at the aggregate.
        """
        # TODO: fill up
        raise NotImplementedError()
        
    ####################################################################
    # Overrides from expedient.clearinghouse.aggregate.models.Aggregate
    def check_status(self):
        try:
            ver = self.proxy.GetVersion()
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False
        return self.available
    
    def add_to_slice(self, slice, next):
        """
        Create a GENISliceInfo instance for this slice if none exists.
        """
        info, created = GENISliceInfo.objects.get_or_create(slice=slice)
        slice.aggregate.add(self)
        return next
    
    def start_slice(self, slice):
        return self.create_sliver(slice)
        
    def stop_slice(self, slice):
        return self.delete_sliver(slice)
