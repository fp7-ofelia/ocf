'''
Created on Jul 4, 2010

@author: jnaous
'''

import re
from django.db import models
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.common.utils import certtransport
from django.conf import settings
import xmlrpclib
from expedient.clearinghouse.slice.models import Slice
from expedient.clearinghouse.geni.utils import create_slice_urn, create_x509_cert,\
    create_slice_credential, get_or_create_user_cert, get_user_key_fname,\
    get_user_cert_fname, get_ch_urn
from django.db.models import signals
import logging
import traceback
from urlparse import urlparse
from expedient.common.utils.transport import TestClientTransport
from expedient.common.federation.sfa.trust.gid import GID
from expedient.common.tests.utils import test_to_http
from expedient.common.middleware import threadlocals
from expedient.common.timer.models import Job
from expedient.common.timer.exceptions import JobAlreadyScheduled

logger = logging.getLogger("geni.models")

SSH_KEY_SIZE = 2048

class GENISliceInfo(models.Model):
    """
    Holds information about the slice that's relevant for the GENI API.
    
    @ivar slice: The slice to which this information belongs.
    @type slice: OneToOneField to L{Slice}.
    @ivar slice_urn: the slice's unique resource name. This will be
        automatically created in the __init__ function if not given.
    @type slice_urn: a string.
    @ivar slice_gid: the slice's certificate. This will be
        automatically created in the __init__ function if not given.
    @type slice_gid: a string.
    @ivar ssh_public_key: Public ssh key in base64. Can be None.
    @type ssh_public_key: string or None.
    @ivar ssh_private_key: Private ssh key in base64, possibly encrypted.
        See L{generate_ssh_keys}. Can be None.
    @type ssh_private_key: string or None.
    """
    slice = models.OneToOneField(
        Slice, related_name="geni_slice_info")
    slice_urn = models.CharField(max_length=256)
    slice_gid = models.TextField("Slice's GID", editable=False)
    ssh_public_key = models.TextField(
        "Slice's SSH public key", editable=False, blank=True, null=True)
    ssh_private_key = models.TextField(
        "Slice's SSH private key", editable=False, blank=True, null=True)
    
    def __init__(self, *args, **kwargs):
        urn = kwargs.setdefault("slice_urn", create_slice_urn())
        kwargs.setdefault(
            "slice_gid", create_x509_cert(urn)[0].save_to_string())
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
            "ssh-rsa %s auto-generated Expedient key" % (key.get_base64())
        
    def login_username(self):
        """
        Get the PlanetLab login username from the slice URN.
        """
        parts = self.slice_urn.split("+")
        name = parts[-1]
        name = re.sub(r"[^0-9a-z_]", "", name)
        prefix = parts[1]
        base = prefix.split(":")[-1]
        return base+"_"+name

def _add_geni_slice_info(sender, instance=None, created=None, **kwargs):
    """Called to create a slice info for a new Slice instance.
    
    Mainly so that all slices have a slice_urn associated.
    """
    if created:
        GENISliceInfo.objects.create(slice=instance)

# Receive signal when object of type "Slice" is ready
from django.dispatch import Signal
post_object_ready = Signal()    
post_object_ready.connect(_add_geni_slice_info, Slice)
#signals.post_save.connect(_add_geni_slice_info, Slice)

class GENIAggregate(Aggregate):
    """
    Implements a generic GCF-based aggregate manager to simplify adding
    GCF-based plugins.
    """
    url = models.CharField(max_length=200)
    
    class URLNotDefined(Exception):
        pass
    
    def _get_client(self, cert_fname, key_fname):
        try:
            u = self.url
        except AttributeError:
            raise self.URLNotDefined("URL not set.")
        if not u:
            raise self.URLNotDefined("URL not set.")
        
        parsed = urlparse(u.lower())
        if parsed.scheme == "test":
            user_cert = GID(filename=cert_fname).save_to_string()
            transport = TestClientTransport(defaults={
                "REMOTE_USER": user_cert, "SSL_CLIENT_CERT": user_cert})
            proxy = xmlrpclib.ServerProxy(
                test_to_http(u),
                transport=transport,
            )
        else:
            transport = certtransport.SafeTransportWithCert(
                keyfile=key_fname,
                certfile=cert_fname)
            proxy = xmlrpclib.ServerProxy(u, transport=transport)
        return proxy
        
    def get_user_client(self, user):
        """Get a client to talk to the aggregate as the user."""
        return self._get_client(
            get_user_cert_fname(user), get_user_key_fname(user))
    
    def get_expedient_client(self):
        """Get a client to talk to the aggregate as Expedient."""
        return self._get_client(
            settings.GCF_X509_CH_CERT, settings.GCF_X509_CH_KEY)
    
    @classmethod
    def get_am_cred(cls):
        """
        Get the slice authority credentials to use for AM calls.
        
        @return: GENI credential string.
        """
        slice_urn = create_slice_urn()
        slice_gid, _ = create_x509_cert(slice_urn) 
        user_gid = GID(filename=settings.GCF_X509_CH_CERT)
        ucred = create_slice_credential(user_gid, slice_gid)
        return ucred.save_to_string()
    
    def get_slice_cred(self, slice, user):
        info = slice.geni_slice_info
        user_cert = get_or_create_user_cert(user)
        return create_slice_credential(
            user_cert, GID(string=str(info.slice_gid))
        ).save_to_string()
        
    def _create_sliver(self, slice):
        """
        Corresponds to the CreateSliver call of the GENI aggregate API.
        Creates a sliver on the aggregate from this slice.
        """
        logger.debug("Called GENIAggregate._create_sliver")

        user = threadlocals.get_thread_locals()["user"]
        
        rspec = self.as_leaf_class()._to_rspec(slice)
        info = GENISliceInfo.objects.get(slice=slice)

        slice_cred = self.get_slice_cred(slice, user)
        proxy = self.get_user_client(user)

        try:
            _ = proxy.CreateSliver(
                info.slice_urn, [slice_cred], rspec,
                [dict(name=settings.GCF_BASE_NAME,
                      urn=get_ch_urn(),
                      keys=[info.ssh_public_key])
                 ]
            )
        except Exception as e:
            logger.error(traceback.format_exc())
            raise Exception("Error creating sliver: %s" % e)
    
        # TODO: parse reserved slice to see errors and such
    
    def _delete_sliver(self, slice):
        """
        Corresponds to the DeleteSliver call of the GENI aggregate API.
        Stop and delete slice at the aggregate.
        """
        user = threadlocals.get_thread_locals()["user"]
        info = GENISliceInfo.objects.get(slice=slice)
        # Get the user's cert
        slice_cred = self.get_slice_cred(slice, user)
        proxy = self.get_user_client(user)

        try:
            ret = proxy.DeleteSliver(
                info.slice_urn, [slice_cred])
        except Exception as e:
            logger.error(traceback.format_exc())
            raise Exception("Error deleting sliver: %s" % e)
    
        return ret
        
    def sliver_status(self, slice):
        """
        Corresponds to the SliverStatus call of the GENI aggregate API.
        Returns the sliver's status at the aggregate.
        """
        # TODO: fill up
        raise NotImplementedError()
        
    def update_resources(self):
        """Parse the rspec and update resources in the database.
        
        Pull the rspec from the aggregate and parse it into resources stored
        in the database.
        """
        proxy = self.get_expedient_client()
        rspec = proxy.ListResources(
            [self.get_am_cred()],
            {"geni_compressed": False, "geni_available": True})
        
        logger.debug("Got rspec:\n%s" % rspec)

        self._from_rspec(rspec)
        
        try:
            Job.objects.schedule(
                settings.GENI_AGGREGATE_UPDATE_PERIOD,
                self.update_resources,
            )
        except JobAlreadyScheduled:
            pass
            
        
    #####################################################################
    # Overrides from expedient.clearinghouse.aggregate.models.Aggregate #
    #####################################################################

    def check_status(self):
        proxy = self.get_expedient_client()
        try:
            ver = proxy.GetVersion()
        except Exception as e:
            logger.error(traceback.format_exc())
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
        super(GENIAggregate, self).add_to_slice(slice, next)
        
        info, _ = GENISliceInfo.objects.get_or_create(
            slice=slice,
        )
        
        if not info.ssh_private_key or not info.ssh_public_key:
            info.generate_ssh_keys()
            info.save()
        
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
    
    def _from_rspec(self, rspec):
        """Parse the rspec and update resources in the database.
        
        @param rspec: The rspec describing the remote resources.
        @type rspec: XML C{str}
        """
        raise NotImplementedError()

