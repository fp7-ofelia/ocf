from foam.sfa.rspecs.elements.element import Element
 
class Install(Element):
    fields = [
        'file_type',
        'url',
        'install_path',
    ]
