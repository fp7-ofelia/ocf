from common.api.generic import Generic
from common.api.backend import Backend
from modules.aggregate.models import Aggregate as AggregateModel
from django.shortcuts import get_object_or_404

class Aggregate(Generic):

    default_backend = AggregateModel

    def __init__(self):
        self.backend = Aggregate.default_backend
        self.api_type = "Aggregate"
        Generic(self.backend,self.api_type)

    def get_aggregates(self):
        return self.backend.get_aggregates()

    def get_object_or_404(self,id):
        return get_object_or_404(self.backend,id).as_leaf_class()


   
   
