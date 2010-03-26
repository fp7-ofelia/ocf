from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class Aggregate(models.Model):
    '''Holds information about an aggregate. Needs to be extended by plugins.'''
    
    name = models.CharField(max_length=200, unique=True)
    
    # The fields below are used to relate the parent Aggregate type
    # to the actual Aggregate type (a child or grandchild...) 
    # that should be used.
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    
    class Meta:
        abstract = True
        
    def __init__(self, *args, **kwargs):
        if 'content_object' not in kwargs:
            kwargs['content_object'] = self
        super(Aggregate, self).__init__(*args, **kwargs)
        
    def __getattribute__(self, name):
        return self.content_object.__getattr__(name)
    
    def reload_resources(self):
        '''Reload the available resources into the DB'''
        raise NotImplementedError()

    def create_slice(self, slice_id, *args, **kwargs):
        '''Create a new slice with the given slice_id
        and the resources specified. Does not actually
        make the reservation. Use start_slice for that.
        
        Params:
            slice_id: unique id to give to the slice
        '''
        raise NotImplementedError()
    
    def start_slice(self, slice_id, *args, **kwargs):
        '''Reserves/allocates the resources in the aggregate
        
        Params:
            slice_id: id of the slice to start
        '''
        raise NotImplementedError()
    
    def delete_slice(self, slice_id, *args, **kwargs):
        '''Delete slice with given slice_id
        
        Params:
            slice_id: id of slice to delete
        '''
        raise NotImplementedError()
    
    def stop_slice(self, slice_id, *args, **kwargs):
        '''Stops running the slice, but does not delete it.
        
        Params:
            slice_id: id of the slice to stop
        '''
        raise NotImplementedError()
