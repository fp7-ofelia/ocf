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
import uuid
from gcf.geni.ch import publicid_to_urn

class GENIAggregateSliceInfo(models.Model):
    """
    Holds information about the slice that's relevant for the GENI API.
    
    @ivar slice: The slice to which this information belongs.
    @type slice: OneToOneField to L{Slice}.
    @ivar slice_urn: the slice's unique resource name. This will be
        automatically created in the __init__ function if not given.
    @type slice_urn: a string.
    @ivar slice_credential: the slice's access credential. This will be
        automatically created in the __init__ function if not given.
    @type slice_credential: a string.
    """
    slice = models.OneToOneField(
        Slice, related_name="geni_aggregate_slice_info")
    slice_urn = models.CharField(max_length=1024)
    slice_credential = models.TextField()
    
    def __init__(self, *args, **kwargs):
        super(GENIAggregateSliceInfo, self).__init__(*args, **kwargs)
        slice_uuid = uuid.uuid4()
        urn = publicid_to_urn(settings.GENI_PUBLIC_ID)
        # TODO: fill this up once GPO finishes the new gcf.
        

class GENIAggergate(Aggregate):
    url = models.URLField(max_length=200)
    
    class URLNotDefined(Exception): pass
    
    def __init__(self, *args, **kwargs):
        super(Aggregate, self).__init__(*args, **kwargs)

        try:
            u = self.url
        except AttributeError:
            raise self.URLNotDefined("Define the url attribute when init'ing\
 the GENIAggregate model.")
        
        transp = certtransport.SafeTransportWithCert(
            keyfile=settings.GENI_x509_KEY, certfile=settings.GENI_x509_CERT)

        self.proxy = xmlrpclib.ServerProxy(u, transport=transp)
    
    def to_rspec(self, slice):
        """
        Change this slice into an rspec for this aggregates
        """
        raise NotImplementedError()
    
    def list_resources(self, rspec):
        """
        Parse the rspec and update resources in the database.
        """
        raise NotImplementedError()
    
    def create_sliver(self, slice):
        """
        Corresponds to the CreateSliver call of the GENI aggregate API.
        Creates a sliver on the aggregate from this slice.
        """
        
        rspec = self.as_leaf_class().to_rspec(slice)
        info = slice.geni_aggregate_slice_info
        
        try:
            reserved = self.proxy.CreateSliver(
                info.slice_urn, [info.slice_credential], rspec)
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise Exception("Error creating sliver: %s" % e)
    
        # TODO: parse reserved slice to see errors and such
    
    def delete_sliver(self, slice):
        """
        Corresponds to the DeleteSliver call of the GENI aggregate API.
        Stop and delete slice at the aggregate.
        """
        
        rspec = self.as_leaf_class().to_rspec(slice)
        info = slice.geni_aggregate_slice_info
        
        try:
            ret = self.proxy.DeleteSliver(
                info.slice_urn, [info.slice_credential], rspec)
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
        