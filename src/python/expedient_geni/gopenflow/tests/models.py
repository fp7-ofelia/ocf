'''
Created on Oct 6, 2010

@author: jnaous
'''
from django.db import models
from openflow.plugin.gapi import gapi

class DummyOFAggregate(models.Model):
    adv_rspec = models.XMLField()
    resv_rspec = models.XMLField(null=True, blank=True)
    
    def snapshot_switches(self):
        self.adv_rspec = gapi.ListResources({}, None)
        self.save()
