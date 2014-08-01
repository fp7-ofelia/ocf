from xml.dom.minidom import parseString
from federation.rspecs.src.geni.v3.container.aggregate import Aggregate
from federation.rspecs.src.geni.v3.container.resource import Resource
from federation.rspecs.src.geni.v3.container.slice import Slice
from federation.rspecs.src.geni.v3.container.sliver import Sliver

class ParserManager:
    
    def __init__(self):
        pass
    
    def parse_request_rspec(self, slice_urn, rspec, slice_expiration=None, slice=None):
        am = Aggregate()
        if slice == None:
            slice = Slice()
        slice.set_urn(slice_urn)
        
        rspec_dom = parseString(rspec)
        nodes = rspec_dom.getElementsByTagName('node')
        print "Nodes:",nodes
        sliver = self.parse_nodes(nodes)
        slice.set_slivers = [sliver]
        print "---------SLICE,", slice
        am.set_slices([slice])
        return am
    
    def parse_nodes(self, nodes):
        sliver = Sliver()
        vms = list()
        for element in nodes:
            node = element.attributes
            resource = Resource()
            if node.has_key('client_id'):
                resource.set_id(node.get('client_id').value)
            if node.has_key('interfaces'):
                pass #Implement when needed    
            if node.has_key('services'):
                pass #Implement when needed
            vms.append(resource)
        sliver.set_resources(vms)
        return sliver
       
