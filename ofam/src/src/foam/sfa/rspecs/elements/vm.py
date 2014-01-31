from foam.sfa.rspecs.elements.element import Element

class VM(Element):
    fields = [
        'name',
        'uuid',
	'state',
        'project-id',
        'slice-id',
        'operating-system-type',
	'operating-system-version',
        'operating-system-distribution',
        'virtualization-type',
	'server-id',
	'hd-setup-type',
	'hd-origin-path',
	'virtualization-setup-type',
	'memory-mb',
	'interfaces'
    ]

