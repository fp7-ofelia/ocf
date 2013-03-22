from django.db import models

class iFace(models.Model):
    
    class Meta:
        """Meta Class for your model."""
        app_label = 'vt_plugin'


    name = models.CharField(max_length = 32, default="", blank = True, null=True)
    isMgmt = models.BooleanField()
    mac = models.CharField(max_length = 17, default="", blank = True, null=True)
    ip =models.IPAddressField(blank = True, null=True)
    gw =models.IPAddressField(blank = True, null=True)
    mask =models.IPAddressField(blank = True, null=True)
    dns1 =models.IPAddressField(blank = True, null=True)
    dns2 =models.IPAddressField(blank = True, null=True)
    bridgeIface = models.CharField(max_length = 32, default="", blank = True, null=True)
    
