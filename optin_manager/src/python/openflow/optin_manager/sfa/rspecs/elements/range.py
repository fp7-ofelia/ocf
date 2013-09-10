from openflow.optin_manager.sfa.rspecs.elements.element import Element

class Range(Element):

    fields = [
        'type',
	'name',
	'start_value',
	'end_value',
	'is_global'
    ]
