#from django.db import models
from foam.ethzlegacyoptinstuff.legacyoptin.flowspaceutils import int_to_mac, int_to_dotted_ip

class FlowSpace(object): #(models.Model):
    mac_src_s           = None #models.BigIntegerField("Start Source MAC address", null=True, default=0x000000000000)
    mac_src_e           = None #models.BigIntegerField("End Source MAC address", null=True, default=0xFFFFFFFFFFFF)
    mac_dst_s           = None #models.BigIntegerField("Start Destination MAC address" , null=True, default=0x000000000000)
    mac_dst_e           = None #models.BigIntegerField("End Destination MAC address" , null=True, default=0xFFFFFFFFFFFF)
    eth_type_s          = None #models.IntegerField("Start Ethernet Type" , null=True, default=0x0000)
    eth_type_e          = None #models.IntegerField("End Ethernet Type" , null=True, default=0xFFFF)
    vlan_id_s           = None #models.IntegerField("Start Vlan ID" , null=True, default=0x000)
    vlan_id_e           = None #models.IntegerField("End Vlan ID" , null=True, default=0xFFF)
    ip_src_s            = None #models.BigIntegerField("Start Source IP Address" , null=True, default=0x00000000)
    ip_src_e            = None #models.BigIntegerField("End Source IP Address" , null=True, default=0xFFFFFFFF)
    ip_dst_s            = None #models.BigIntegerField("Start Destination IP Address" , null=True, default=0x00000000)
    ip_dst_e            = None #models.BigIntegerField("End Destination IP Address" , null=True, default=0xFFFFFFFF)
    ip_proto_s          = None #models.IntegerField("Start IP Protocol Number" , null=True, default=0x00)
    ip_proto_e          = None #models.IntegerField("End IP Protocol Number" , null=True, default=0xFF)
    tp_src_s            = None #models.IntegerField("Start Source Transport Port" , null=True, default=0x0000)
    tp_src_e            = None #models.IntegerField("End Source Transport Port" , null=True, default=0xFFFF)
    tp_dst_s            = None #models.IntegerField("Start Destination Transport Port" , null=True, default=0x0000)
    tp_dst_e            = None #models.IntegerField("End Destination Transport Port" , null=True, default=0xFFFF)

    def stringify(self):
        return "%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s"%(
                    self.mac_src_s,self.mac_src_e,
                    self.mac_dst_s,self.mac_dst_e,
                    self.vlan_id_s,self.vlan_id_e,
                    self.ip_src_s,self.ip_src_e,
                    self.ip_dst_s,self.ip_dst_e,
                    self.ip_proto_s,self.ip_proto_e,
                    self.tp_src_s,self.tp_src_e,
                    self.tp_dst_s,self.tp_dst_e,
                    )                      
          
    def __unicode__(self):
        expression = ""
        if (self.mac_src_s  == self.mac_src_e):
            expression = expression + ("MAC Source Addr: %s, " % (int_to_mac(self.mac_src_s)))
        elif (self.mac_src_s > 0 or self.mac_src_e < 0xFFFFFFFFFFFF):
            expression = expression + ("MAC Source Addr: %s-%s, " % (int_to_mac(self.mac_src_s), int_to_mac(self.mac_src_e)))
        if (self.mac_dst_s  == self.mac_dst_e):
            expression = expression + ("MAC Destination Addr: %s, " % (int_to_mac(self.mac_dst_s)))
        elif (self.mac_dst_s > 0 or self.mac_dst_e < 0xFFFFFFFFFFFF): 
            expression = expression + ("MAC Destination Addr: %s-%s, " % (int_to_mac(self.mac_dst_s), int_to_mac(self.mac_dst_e))) 
        if (self.eth_type_s == self.eth_type_e): 
            expression = expression + ("Eth Type: 0x%x, " % (self.eth_type_s)) 
        elif (self.eth_type_s > 0 or self.eth_type_e < 0xFFFF): 
            expression = expression + ("Eth Type: 0x%x-0x%x, " % (self.eth_type_s,self.eth_type_e)) 
        if (self.vlan_id_s == self.vlan_id_e): 
            expression = expression + ("VALN id: %d, " % (self.vlan_id_s)) 
        elif (self.vlan_id_s > 0 or self.vlan_id_e < 0xFFF): 
            expression = expression + ("VALN id: %d-%d, " % (self.vlan_id_s,self.vlan_id_e)) 
        if (self.ip_src_s == self.ip_src_e):    
            expression = expression + ("IP Source Addr: %s, " % (int_to_dotted_ip(self.ip_src_s)))
        elif (self.ip_src_s > 0 or self.ip_src_e < 0xFFFFFFFF):    
            expression = expression + ("IP Source Addr: %s-%s, " % (int_to_dotted_ip(self.ip_src_s), int_to_dotted_ip(self.ip_src_e)))
        if (self.ip_dst_s == self.ip_dst_e):    
            expression = expression + ("IP Destination Addr: %s, " % (int_to_dotted_ip(self.ip_dst_s)))
        elif (self.ip_dst_s > 0 or self.ip_dst_e < 0xFFFFFFFF):    
            expression = expression + ("IP Destination Addr: %s-%s, " % (int_to_dotted_ip(self.ip_dst_s), int_to_dotted_ip(self.ip_dst_e)))
        if (self.ip_proto_s == self.ip_proto_e):    
            expression = expression + ("IP Protocol Number: %s, " % (self.ip_proto_s)) 
        elif (self.ip_proto_s > 0 or self.ip_proto_e < 0xFF):    
            expression = expression + ("IP Protocol Number: %s-%s, " % (self.ip_proto_s, self.ip_proto_e)) 
        if (self.tp_src_s == self.tp_src_e):    
            expression = expression + ("Transport Source Port: %s, " % (self.tp_src_s))
        elif (self.tp_src_s > 0 or self.tp_src_e < 0xFFFF):    
            expression = expression + ("Transport Source Port: %s-%s, " % (self.tp_src_s, self.tp_src_e))
        if (self.tp_dst_s == self.tp_dst_e):    
            expression = expression + ("Transport Destination Port: %s, " % (self.tp_dst_s))
        if (self.tp_dst_s > 0 or self.tp_dst_e < 0xFFFF):    
            expression = expression + ("Transport Destination Port: %s-%s, " % (self.tp_dst_s, self.tp_dst_e))
        if expression == "":
            expression = "All"
        return expression
                     
#        return ("MAC Source Addr: %s-%s , MAC Destination Addr: %s-%s # IP Source Addr: %s-%s , \
#            IP Destination Addr: %s-%s # TP Source Port: %d-%d , TP Destination Port: %d-%d" % 
#        (int_to_mac(self.mac_src_s), int_to_mac(self.mac_src_e), int_to_mac(self.mac_dst_s), int_to_mac(self.mac_dst_e),
#         int_to_dotted_ip(self.ip_src_s), int_to_dotted_ip(self.ip_src_e), int_to_dotted_ip(self.ip_dst_s), int_to_dotted_ip(self.ip_dst_e),
#          self.tp_src_s, self.tp_src_e, self.tp_dst_s, self.tp_dst_e) )   
        
    class Meta:
        abstract = True

 
