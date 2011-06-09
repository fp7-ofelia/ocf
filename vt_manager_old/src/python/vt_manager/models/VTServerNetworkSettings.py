from django.db import models

class VTServerNetworkingSettings(models.Model):
    """Virtualization Server Networking settings class"""

    class Meta:
        """Meta Class for your model."""
        app_label = 'vt_manager'


    ipRange = models.IPAddressField(default = "", verbose_name = "VM IP range")
    mask = models.IPAddressField(default = "", verbose_name = "Subnet mask")
    gw = models.IPAddressField(default= "", verbose_name = "Gateway")
    dns1 = models.IPAddressField(default = "", verbose_name = "DNS 1")
    dns2 =  models.IPAddressField(default = "", verbose_name = "DNS 2", blank = True, null = True)

    def validate_ip(value):
        def error():
            raise ValidationError(
                "Enter a valid IP / mask",
                code="invalid",
            )
        cntrlr_url_re = re.compile("(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)")
        m = cntrlr_url_re.match(value)
        if not m:
            error()

