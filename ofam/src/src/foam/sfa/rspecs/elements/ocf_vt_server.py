from foam.sfa.rspecs.elements.element import Element

class OcfVtServer(Element):

    fields = [
        'name',
	'operating_system_type',
	'operating_system_distribution',
	'operating_system_version',
	'virtualization_technology',
	'cpus_number',
	'cpu_frequency',
	'memory',
	'hdd_space_GB',
	'agent_url',
    ]

