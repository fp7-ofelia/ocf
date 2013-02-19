from vt_manager.communication.sfa.rspecs.elements.element import Element

class DiskImage(Element):
    fields = [
        'name',
        'os',
        'version',
        'description',
    ]        
