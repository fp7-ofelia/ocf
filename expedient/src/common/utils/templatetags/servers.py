"""
Filters for Django template system (Jinja).
Functionality in this file is related to servers and VMs.

@date: Mar 19, 2013
@author: CarolinaFernandez
"""

from django import template

register = template.Library()

@register.filter
def number_vms_inside_server_for_slice(server, slice_uuid):
    """
    Returns number of VMs given a server and a slice.
    """
    vms_inside = 0
    for vm in server.vtserver.vms.all():
        if server.uuid == vm.serverID and vm.sliceId == slice_uuid:
            vms_inside+=1
    return vms_inside

