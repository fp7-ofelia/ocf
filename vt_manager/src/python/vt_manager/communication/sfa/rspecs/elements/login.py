from vt_manager.communication.sfa.rspecs.elements.element import Element

class Login(Element):
    fields = [
        'authentication',
        'hostname',
        'port',
        'username'
    ]
