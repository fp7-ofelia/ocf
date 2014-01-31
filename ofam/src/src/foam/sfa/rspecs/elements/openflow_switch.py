from foam.sfa.rspecs.elements.element import Element

class OpenFlowSwitch(Element):

    fields = [
        'component_id',
        'component_manager_id',
	'dpid',
	'port',
    ]

