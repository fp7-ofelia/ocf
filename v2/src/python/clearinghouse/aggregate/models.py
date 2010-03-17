from django.db import models

class Aggregate(models.Model):
    '''Holds information about an aggregate'''
    
    name = models.CharField(max_length=200, unique=True)
    
    class Meta:
        abstract = True
    
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
