'''
Created on May 12, 2010

@author: jnaous
'''

from django.db import models

import logging
logger = logging.getLogger("DummyOMModels")

def long_to_dpid(l):
    import re
    if type(l) == str and ":" in str:
        return l
    s = "%016x" % long(l)
    m = re.findall("\w\w", s)
    return ":".join(m)

class DummyOM(models.Model):
    '''
    A dummy OM with a set of unique links.
    '''
    
    def get_switches(self):
        return [s.get_as_tuple() for s in self.dummyomswitch_set.all()]
    
    def get_links(self):
        return [link.get_as_tuple() for link in self.dummyomlink_set.all()]
        
    def populate_links(self, num_switches, num_links, use_random=False):
        '''Create switches and random links'''
        import random
        
        if not use_random:
            random.seed(0)
        
        if num_switches >= 1000:
            raise Exception("Can only create less than 1000 dpids per DummyOM")
        
        for l in range(num_switches):
            DummyOMSwitch.objects.create(
                dpid=long_to_dpid(self.id*1024+l),
                nPorts=8,
                portList=",".join(map(str, range(0,8))),
                om=self,
            )
            
        dpids = self.dummyomswitch_set.all().values_list("dpid", flat=True)
        
        for l in range(num_links):
            src, dst = random.sample(dpids, 2)
            src_port = random.randint(0, 7)
            dst_port = random.randint(0, 7)
            DummyOMLink.objects.create(
                src_dpid=src,
                src_port=src_port,
                dst_dpid=dst,
                dst_port=dst_port,
                om=self,
            )
            DummyOMLink.objects.create(
                src_dpid=dst,
                src_port=dst_port,
                dst_dpid=src,
                dst_port=src_port,
                om=self,
            )
            
    def kill_dpid(self, dpid=None, use_random=False):
        '''
        Remove all links associated with a dpid. If dpid is None, chooses a
        dpid. If use_random is False, chooses the dpid deterministically. 
        Returns killed dpid.
        '''
        import random

        if not use_random:
            random.seed(0)
        
        switches = self.get_switches()
        if dpid == None:
            dpid = random.choice(switches)[0]

        self.dummyomlink_set.filter(src_dpid=dpid).delete()
        self.dummyomlink_set.filter(dst_dpid=dpid).delete()
        self.dummyomswitch_set.get(dpid=dpid).delete()

        return dpid

class DummyOMLink(models.Model):
    '''
    A link used by the dummy OM fixtures.
    '''
    src_dpid = models.CharField(max_length=100)
    src_port = models.IntegerField()
    dst_dpid = models.CharField(max_length=100)
    dst_port = models.IntegerField()
    om = models.ForeignKey(DummyOM)
    
    def get_as_tuple(self):
        return [str(self.src_dpid),
                str(self.src_port),
                str(self.dst_dpid),
                str(self.dst_port), {}] 
    
class DummyOMSwitch(models.Model):
    '''
    A switch used by the dummy OM fixtures.
    '''
    dpid = models.CharField(max_length=100)
    om = models.ForeignKey(DummyOM)
    nPorts = models.IntegerField()
    portList = models.CharField(max_length=1024)

    def get_as_tuple(self):
        t = [self.dpid, {"nPorts": str(self.nPorts), "portList": str(self.portList)}]
        return t
    
class DummyOMSlice(models.Model):
    '''
    A slice used by the dummy OM fixtures.
    '''
    slice_id = models.CharField(max_length=200)
    project_name = models.CharField(max_length=200)
    project_description = models.TextField()
    slice_name = models.CharField(max_length=200)
    slice_description = models.TextField()
    controller_url = models.CharField(max_length=200)
    owner_email = models.CharField(max_length=200)
    owner_password = models.CharField(max_length=200)
    switch_slivers = models.TextField()
    om = models.ForeignKey(DummyOM)
    
class DummyCallBackProxy(models.Model):
    '''
    A dummy callback server proxy to call back the CH on
    topology changes (not done automatically).
    '''
    url = models.CharField(max_length=200)
    cookie = models.CharField(max_length=1024)
    username = models.CharField(max_length=1024)
    om = models.OneToOneField(DummyOM)
    
    def call_back(self):
        from xmlrpclib import ServerProxy
        logger.debug("DummyCallBackProxy.call_back at %s with cookie %s" % (
            self.url, self.cookie))
        s = ServerProxy(self.url)
        s.topology_changed(self.cookie)
