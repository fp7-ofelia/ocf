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
from expedient_geni import management

SSH_KEY_SIZE = 2048

class GENISliceInfo(models.Model):
    """
    Holds information about the slice that's relevant for the GENI API.
    
    @ivar slice: The slice to which this information belongs.
    @type slice: OneToOneField to L{Slice}.
    @ivar slice_urn: the slice's unique resource name. This will be
        automatically created in the __init__ function if not given.
    @type slice_urn: a string.
    @ivar ssh_public_key: Public ssh key in base64. Can be None.
    @type ssh_public_key: string or None.
    @ivar ssh_private_key: Private ssh key in base64, possibly encrypted.
        See L{generate_ssh_keys}. Can be None.
    @type ssh_private_key: string or None.
    @ivar slice_cred: Credentials to use for the slice
    @type slice_cred: string
    """
    slice = models.OneToOneField(
        Slice, related_name="geni_slice_info")
    slice_urn = models.CharField(max_length=1024)
    ssh_public_key = models.TextField(
        "Slice's SSH public key", editable=False, blank=True, null=True)
    ssh_private_key = models.TextField(
        "Slice's SSH private key", editable=False, blank=True, null=True)
    slice_cred = models.TextField(
        "Slice credentials", editable=False, blank=True, null=True)
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("slice_urn", management.create_slice_urn())
        super(GENISliceInfo, self).__init__(*args, **kwargs)
        
    def generate_ssh_keys(self, password=None):
        """
        Set the C{ssh_public_key} and C{ssh_private_key} attributes to be
        new keys. Note that the keys are stored in base64.
        
        @parameter password: password to use to encrypt the private key
        @type password: string
        """
        from paramiko import RSAKey
        from StringIO import StringIO
        
        key = RSAKey.generate(SSH_KEY_SIZE)
        
        output = StringIO()
        key.write_private_key(output, password=password)
        self.ssh_private_key = output.getvalue()
        output.close()
        
        self.ssh_public_key = \
            "ssh-rsa %s auto-generated Expedient key" % (key. get_base64())
        
        
    def generate_slice_cred(self):
        """
        Create credentials to use for the slice.
        """
        from gcf.sfa.trust import gid
        slice_gid, keys = management.create_slice_gid(self.slice_urn)
        user_gid = gid.GID(filename=settings.GCF_X509_CH_CERT)
        cred = management.create_slice_credential(user_gid, slice_gid)
        self.slice_cred = cred.save_to_string()
        
    def login_username(self):
        """
        Get the PlanetLab login username from the slice URN.
        """
        
        parts = self.slice_urn.split("+")
        name = parts[-1]
        prefix = parts[1]
        base = prefix.partition(":")[2]
        return base+"_"+name    

class GENIAggregate(Aggregate):
    """
    Implements a generic GCF-based aggregate manager to simplify adding
    GCF-based plugins.
    """
    url = models.CharField(max_length=200)
    
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
            return self.proxy
        else:
            raise AttributeError, name
    
    @classmethod
    def get_am_cred(cls):
        """
        Get the slice authority credentials to use for AM calls.
        
        @return: GENI credential string.
        """
        f = open(settings.GCF_NULL_SLICE_CRED)
        am_cred = f.read()
        f.close()
        return am_cred
    
    def _create_sliver(self, slice):
        """
        Corresponds to the CreateSliver call of the GENI aggregate API.
        Creates a sliver on the aggregate from this slice.
        """
        
        rspec = self.as_leaf_class()._to_rspec(slice)
        info = slice.geni_slice_info
        
        try:
            reserved = self.proxy.CreateSliver(
                info.slice_urn, [info.slice_cred], rspec,
                [dict(name=settings.GCF_URN_PREFIX,
                      urn="urn:publicid:IDN+%s+%s+%s" % (
                            settings.GCF_URN_PREFIX, "authority", "ch"),
                      keys=[info.ssh_public_key])
                 ]
            )
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
        info = slice.geni_slice_info
        try:
            ret = self.proxy.DeleteSliver(
                info.slice_urn, [info.slice_cred])
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
        
    #####################################################################
    # Overrides from expedient.clearinghouse.aggregate.models.Aggregate #
    #####################################################################

    def check_status(self):
        try:
            ver = self.proxy.GetVersion()
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False
        return self.available
    
    def start_slice(self, slice):
        super(GENIAggregate, self).start_slice(slice)
        return self._create_sliver(slice)
        
    def stop_slice(self, slice):
        super(GENIAggregate, self).stop_slice(slice)
        return self._delete_sliver(slice)
    
    def add_to_slice(self, slice, next):
        """
        Make sure that there's only one GENI slice info.
        """
        info, created = GENISliceInfo.objects.get_or_create(
            slice=slice,
        )
        if created:
            info.generate_ssh_keys()
            info.generate_slice_cred()
            info.save()
            
        slice.aggregates.add(self)
            
        return next

    #####################################################################
    # Subclasses must override the below functions                      #
    #####################################################################
    
    def _to_rspec(self, slice):
        """Change this slice into an rspec for this aggregates
        
        Transform the slice into a reservation RSpec to be used with this
        aggregate.
        
        @param slice: The slice to change into a reservation RSpec
        @type slice: L{expedient.clearinghouse.slice.models.Slice}
        """
        raise NotImplementedError()
    
    def update_resources(self):
        """Parse the rspec and update resources in the database.
        
        Pull the rspec from the aggregate and parse it into resources stored
        in the database.
        """
        raise NotImplementedError()
    