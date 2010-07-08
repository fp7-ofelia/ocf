'''
Created on Jul 4, 2010

@author: jnaous
'''
from django.db import models
from expedient.clearinghouse.resources.models import Resource, Sliver
from expedient.clearinghouse.aggregate.models import Aggregate

class PlanetLabNetwork(models.Model):
    """
    PlanetLab NetSpec.
    """
    name = models.CharField(max_length=100)
    
class PlanetLabLink(models.Model):
    """
    A PlanetLab Rspec LinkSpec.
    """
    type = models.CharField(max_length=60)
    init_params = models.TextField(default="")
    bw = models.IntegerField("Bandwidth")
    min_alloc = models.IntegerField("Minimum allocation")
    max_alloc = models.IntegerField("Maximum allocation")
    network = models.ForeignKey(PlanetLabNetwork, related_name="links")

class PlanetLabNode(Resource):
    '''
    A PlanetLab node.
    '''
    type = models.CharField(max_length=60)
    init_params = models.TextField(default="")
    cpu_min = models.IntegerField()
    cpu_share = models.IntegerField()
    cpu_pct = models.IntegerField()
    disk_max = models.IntegerField()
    network = models.ForeignKey(PlanetLabNetwork, related_name="nodes")
    
class PlanetLabInterface(Resource):
    '''
    A PlanetLab Interface (IfSpec)
    '''
    addr = models.CharField("Address", max_length=200)
    type = models.CharField(max_length=60)
    init_params = models.TextField(default="")
    min_rate = models.IntegerField("Minimum Throughput")
    max_rate = models.IntegerField("Maximum Throughput")
    max_kbyte = models.IntegerField()
    ip_spoof = models.BooleanField("Spoof IP Address?")
    
    link = models.ForeignKey(PlanetLabLink, related_name="endpoints")
    node = models.ForeignKey(PlanetLabNode)

class PlanetLabNodeSliver(Sliver):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
class PlanetLabAggregate(Aggregate):
    