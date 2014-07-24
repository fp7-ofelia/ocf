'''
Created on Oct 6, 2010

@author: jnaous
'''
from django.db import models
from django.conf import settings
from openflow.plugin.gapi import gapi, rspec
from expedient.common.federation.geni.util.urn_util import publicid_to_urn

OTHER_BASENAME ="test//test"
OTHER_PREFIX = publicid_to_urn(
    "IDN %s//%s"
    % (OTHER_BASENAME, settings.OPENFLOW_GCF_BASE_SUFFIX)
)

class DummyOFAggregate(models.Model):
    #adv_rspec = models.XMLField()
    adv_rspec = models.TextField()
    #resv_rspec = models.XMLField(null=True, blank=True)
    resv_rspec = models.TextField(null=True, blank=True)
    
    def snapshot_switches(self):
        self.adv_rspec = gapi.ListResources({}, None)
        self.adv_rspec = self.adv_rspec.replace(
            rspec.OPENFLOW_GAPI_RSC_URN_PREFIX, OTHER_PREFIX)
        self.save()
