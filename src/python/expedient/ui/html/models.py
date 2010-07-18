'''
Created on Jun 19, 2010

@author: jnaous
'''
from django.db import models
from expedient.clearinghouse.slice.models import Slice
from expedient.common.utils import modelfields
from openflow.plugin.models import FlowSpaceRule

class SliceFlowSpace(models.Model):
    """
    Use one flowspace set for the whole slice.
    """
    slice = models.ForeignKey(Slice)
    
    dl_src = modelfields.MACAddressField(
        'MAC Src', blank=True, null=True)
    dl_dst = modelfields.MACAddressField(
        'MAC Dst', blank=True, null=True)
    dl_type = modelfields.LimitedIntegerField(
        'Eth Type', max_value=2**16-1, min_value=0, blank=True, null=True)
    vlan_id = modelfields.LimitedIntegerField(
        'VLAN ID', max_value=2**12-1, min_value=0, blank=True, null=True)
    nw_src = models.IPAddressField(
        'IP Src', blank=True, null=True)
    nw_dst = models.IPAddressField(
        'IP Dst', blank=True, null=True)
    nw_proto = modelfields.LimitedIntegerField(
        'IP Proto', max_value=2**8-1, min_value=0, blank=True, null=True)
    tp_src = modelfields.LimitedIntegerField(
        'L4 Src', max_value=2**16-1, min_value=0, blank=True, null=True)
    tp_dst = modelfields.LimitedIntegerField(
        'L4 Dst', max_value=2**16-1, min_value=0, blank=True, null=True)
    