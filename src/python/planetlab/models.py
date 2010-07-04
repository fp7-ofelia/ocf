'''
Created on Jul 4, 2010

@author: jnaous
'''
from django.db import models
from expedient.clearinghouse.resources.models import Resource

class PlanetLabInterface(models.Model):
    '''
    A PlanetLab Interface (IfSpec)
    '''
    name = models.CharField(max_length=100)
    addr = models.CharField("Address", max_length=200)
    type = models.CharField(max_length=60)
    init_params = models.TextField()
    min_rate = models.IntegerField("Minimum Throughput")
    max_rate = models.IntegerField("Maximum Throughput")
    ip_spoof = models.BooleanField("Spoof IP Address?")
    
    link = models.ForeignKey("PlanetLabLink", related_name="endpoints")
    
class PlanetLabLink(models.Model):
    """
    A PlanetLab Rspec LinkSpec.
    """
    type = models.CharField(max_length=60)
    init_params = models.TextField()
    bw = models.IntegerField("Bandwidth")
    min_alloc = models.IntegerField("Minimum allocation")
    max_alloc = models.IntegerField("Maximum allocation")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

class PlanetLabNode(Resource):
    '''
    A PlanetLab node.
    '''
    
    