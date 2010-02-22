from django.db import models
from clearinghouse.aggregate.models import Aggregate
from clearinghouse.gresource.models import Resource
from clearinghouse.project.models import Project

class Slice(models.Model):
    '''Holds information about reservations across aggregates'''

    # @ivar name: The name of the Slice
    name = models.CharField(max_length=200)
    
    # @ivar aggregates: Set of aggregates the slice uses
    aggregates = models.ManyToManyField(Aggregate)
    
    # @ivar resources: Set of resources in this slice
    resources = models.ManyToManyField(Resource)
    
    # @ivar project: Project in which this slice belongs
    project = models.ForeignKey(Project)
    