'''
Created on May 12, 2010

@author: jnaous
'''

from django.db import models

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
        dpids = []
        dpids += self.dummyomlink_set.values_list('src_dpid', flat=True)
        dpids += self.dummyomlink_set.values_list('dst_dpid', flat=True)
        dpids = set(dpids)
        return [[dpid, {}] for dpid in dpids]
    
    def get_links(self):
        return [[link.src_dpid,
                 link.src_port,
                 link.dst_dpid,
                 link.dst_port, {}] for link in self.dummyomlink_set.all()]
        
    def populate_links(self, num_switches, num_links, use_random=False):
        '''Create switches and random links'''
        import random
        
        if not use_random: random.seed(0)
        
        if num_switches >= 1000:
            raise Exception("Can only create less than 1000 dpids per DummyOM")
        
        dpids = []
        for l in range(num_switches):
            dpids.append(long_to_dpid(self.id*1024+l))
            
        for l in range(num_links):
            src, dst = random.sample(dpids, 2)
            src_port = random.randint(0, 3)
            dst_port = random.randint(0, 3)
            DummyOMLink.objects.create(
                src_dpid=src,
                src_port=src_port,
                dst_dpid=dst,
                dst_port=dst_port,
                om=self,
            )
            
    def kill_dpid(self, dpid=None, use_random=False):
        '''
        Remove all links associated with a dpid. If dpid is None, chooses a
        dpid. If use_random is False, chooses the dpid deterministically. 
        Returns killed dpid.
        '''
        import random

        if not use_random: random.seed(0)
        
        switches = self.get_switches()
        if dpid == None:
            dpid = random.choice(switches)[0]

        self.dummyomlink_set.filter(src_dpid=dpid).delete()
        self.dummyomlink_set.filter(dst_dpid=dpid).delete()

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
        s = ServerProxy(self.url)
        s.topology_changed(self.cookie)
