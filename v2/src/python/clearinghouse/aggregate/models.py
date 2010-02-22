from django.db import models

class Aggregate(models.Model):
    '''Holds information about an aggregate'''
    
    name = models.CharField(max_length=200, unique=True)
    
    class Meta:
        abstract = True
    
    def reload_resources(self):
        '''Reload the available resources into the DB'''
        pass

    def create_slice(self, slice_id, resources):
        '''Create a new slice with the given slice_id
        and the resources specified. Does not actually
        make the reservation. Use start_slice for that.
        
        Params:
            slice_id: unique id to give to the slice
            resources: list of resource ids to create the slice
        '''
        pass
    
    def start_slice(self, slice_id):
        '''Reserves/allocates the resources in the aggregate
        
        Params:
            slice_id: id of the slice to start
        '''
        pass
    
    def delete_slice(self, slice_id):
        '''Delete slice with given slice_id
        
        Params:
            slice_id: id of slice to delete
        '''
        pass
    
    def stop_slice(self, slice_id):
        '''Stops running the slice, but does not delete it.
        
        Params:
            slice_id: id of the slice to stop
        '''
        pass
    
    