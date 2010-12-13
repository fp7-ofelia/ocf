'''
Created on May 15, 2010

@author: jnaous
'''
from django.db import models
from pprint import pprint

class DummyFV(models.Model):
    def populateTopology(self, num_switches, num_links, use_random=False):
        '''Create switches and random links'''
        import random
        from openflow.optin_manager.flowspace.utils import long_to_dpid
        
        if not use_random: random.seed(0)
        
        if num_switches >= 1000:
            raise Exception("Can only create less than 1000 dpids per Dummy")
        
        for l in range(num_switches):
            DummyFVDevice.objects.create(
                dpid=long_to_dpid(self.id*1024+l),
                fv=self,
            )
            
        for l in range(num_links):
            src, dst = random.sample(DummyFVDevice.objects.all(), 2)
            src_port = random.randint(0, 3)
            dst_port = random.randint(0, 3)
            DummyFVLink.objects.create(
                src_dev=src,
                src_port=src_port,
                dst_dev=dst,
                dst_port=dst_port,
                fv=self,
            )

class DummyFVDevice(models.Model):
    dpid = models.CharField(max_length=23)
    fv = models.ForeignKey(DummyFV)

    def __str__(self):
        return self.dpid

class DummyFVLink(models.Model):
    src_dev = models.ForeignKey(DummyFVDevice, related_name="src_links")
    src_port = models.IntegerField()
    dst_dev = models.ForeignKey(DummyFVDevice, related_name="dst_links")
    dst_port = models.IntegerField()
    fv = models.ForeignKey(DummyFV)
    
    def __str__(self):
        return "%s,%s,%s,%s" % (self.src_dev, self.src_port,
                                self.dst_dev, self.dst_port)

class DummyFVSlice(models.Model):
    name = models.CharField(max_length=500)
    password = models.CharField(max_length=1024)
    controller_url = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    fv = models.ForeignKey(DummyFV)
     
class DummyFVRule(models.Model):
    fv = models.ForeignKey(DummyFV)
    match = models.CharField(max_length=2048)
    actions = models.CharField(max_length=200)
    priority = models.IntegerField()
    dpid = models.CharField(max_length=100)
