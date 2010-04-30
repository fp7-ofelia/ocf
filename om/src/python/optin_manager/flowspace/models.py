from django.db import models
from django.contrib import auth


class FlowSpace(models.Model):
    mac_src_s           = models.IntegerField("Start Source MAC address", null=True, default=0x000000000000)
    mac_src_e           = models.IntegerField("End Source MAC address", null=True, default=0xFFFFFFFFFFFF)
    mac_dst_s           = models.IntegerField("Start Destination MAC address" , null=True, default=0x000000000000)
    mac_dst_e           = models.IntegerField("End Destination MAC address" , null=True, default=0xFFFFFFFFFFFF)
    eth_type_s          = models.IntegerField("Start Ethernet Type" , null=True, default=0x0000)
    eth_type_e          = models.IntegerField("End Ethernet Type" , null=True, default=0xFFFF)
    vlan_id_s           = models.IntegerField("Start Vlan ID" , null=True, default=0x000)
    vlan_id_e           = models.IntegerField("End Vlan ID" , null=True, default=0xFFF)
    vlan_priority_s     = models.IntegerField("Start Vlan Priority" , null=True, default=0x0)
    vlan_priority_e     = models.IntegerField("End Vlan Priority" , null=True, default=0x7)
    ip_src_s            = models.IntegerField("Start Source IP Address" , null=True, default=0x00000000)
    ip_src_e            = models.IntegerField("End Source IP Address" , null=True, default=0xFFFFFFFF)
    ip_dst_s            = models.IntegerField("Start Destination IP Address" , null=True, default=0x00000000)
    ip_dst_e            = models.IntegerField("End Destination IP Address" , null=True, default=0xFFFFFFFF)
    ip_proto_s          = models.IntegerField("Start IP Protocol Number" , null=True, default=0x00)
    ip_proto_e          = models.IntegerField("End IP Protocol Number" , null=True, default=0xFF)
    ip_tos_s            = models.IntegerField("Start IP ToS Number" , null=True, default=0x0)
    ip_tos_e            = models.IntegerField("End IP ToS Number" , null=True, default=0x7)
    tp_src_s            = models.IntegerField("Start Source Transport Port" , null=True, default=0x0000)
    tp_src_e            = models.IntegerField("End Source Transport Port" , null=True, default=0xFFFF)
    tp_dst_s            = models.IntegerField("Start Destination Transport Port" , null=True, default=0x0000)
    tp_dst_e            = models.IntegerField("End Destination Transport Port" , null=True, default=0xFFFF)

    class Meta:
        abstract = True

class OptedInFlowSpace(FlowSpace):
    user            = models.ForeignKey(auth.models.User)
    priority        = models.IntegerField()
    #experiment      = models.ForeignKey()

class AdminFlowSpace(FlowSpace):
    admin           = models.ForeignKey(auth.models.User)


class RequestedAdminFlowSpace(FlowSpace):
    user            = models.ForeignKey(auth.models.User, related_name = "admin_fs_requester")
    admin           = models.ForeignKey(auth.models.User, related_name = "admin_fs_approver")
    req_priority    = models.IntegerField()

class RequestedUserFlowSpace(FlowSpace):
    user            = models.ForeignKey(auth.models.User, related_name = "user_fs_requester")
    admin           = models.ForeignKey(auth.models.User, related_name = "user_fs_approver")