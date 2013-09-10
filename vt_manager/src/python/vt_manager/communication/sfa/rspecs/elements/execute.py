from vt_manager.communication.sfa.rspecs.elements.element import Element

class Execute(Element):
    fields = [
        'shell',
        'command',
    ]
