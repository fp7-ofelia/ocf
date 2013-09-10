

class SliceManager:


    @staticmethod
    def list_resources(aggregate, slice_urn=None):
    
        options = dict()
        options['geni_rspec_version'] = aggregate.get_rspec_version()# Should return a dict with {type:"type" version:"version"}
        if not slice == None:
            options['geni_slice_urn'] = slice_urn

        
