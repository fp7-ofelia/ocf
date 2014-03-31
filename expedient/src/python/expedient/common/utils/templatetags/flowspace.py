"""
Filters for Django template system (Jinja).
Functionality in this file is related to OpenFlow FlowSpaces.

@date: Sep 06, 2013
@author: CarolinaFernandez
"""

from django import template

register = template.Library()

@register.filter
def exists_flowspace_for_aggregate(flowspace, aggregate):
#def exists_flowspace_for_slice_and_aggregate(flowspace, slice, aggregate):
	"""
	Checks the existence of a FlowSpace in a given aggregate.
	@param flowspace FlowSpace for a slice
	@param aggregate OpenFlow AM where the FlowSpace is to be checked
	@return whether FlowSpace has been granted for a particular OpenFlow AM
	"""
	exists = False
	for rule in flowspace:
#	for rule in FlowSpaceRule.objects.filter(slivers__slice=slice):
		for sliver in rule.slivers.all():
			if sliver.resource.aggregate.id == aggregate.id:
				exists = True
				break
	return exists

@register.filter
def key(dictionary, key_name):
    try:
        return dictionary[key_name]
    except:
        return ""

