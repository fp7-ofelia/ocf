'''
Created on Jul 4, 2010

@author: jnaous
'''
from django.db import models
from expedient.clearinghouse.resources.models import Resource

class PlanetLabInterface(Resource):
    '''
    A PlanetLab Interface (IfSpec)
    '''
    
    addr = models.CharField("Address", max_length=200)
    type = models.CharField(max_length=60)
    init_params = models.CharField()

class PlanetLabNode(Resource):
    '''
    A PlanetLab node.
    '''
    
    