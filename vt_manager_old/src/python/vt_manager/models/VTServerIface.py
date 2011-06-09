from django.db import models

class VTServerIface(models.Model):
    """Interface for VTServer"""

    class Meta:
        """Meta Class for your model."""
        app_label = 'vt_manager'

    ifaceName = models.CharField(max_length = 128, default="", blank = True, null=True, verbose_name = "Interface Name")
    switchID = models.CharField(max_length = 128, default="", blank = True, null=True, verbose_name = "Switch ID")
    port = models.IntegerField(blank = True, null=True, verbose_name = "Swtich Port")
    idForm = models.IntegerField(blank = True, null=True)
