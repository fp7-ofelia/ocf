from vt_manager.communication.sfa.rspecs.elements.element import Element

class OcfVtServer(Element):

    fields = [
        'name',
	'SO',
	'Memory',
	'HD',
	'Virtualization_type'
    ]

