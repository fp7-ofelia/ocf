from django.db import models

class resourcesHash(models.Model):

    class Meta:
        """Meta Class for your model."""
        app_label = 'vt_manager'

    server = models.ForeignKey('VTServer', editable = False, related_name = 'statistics')
    name = models.CharField(max_length = 512, default="", verbose_name = "Partition name")
    size = models.IntegerField(blank = True, null=True,  default="", editable = False)
    used = models.IntegerField(blank = True, null=True,  default="", editable = False)
    available = models.IntegerField(blank = True, null=True,  default="", editable = False)
    used_ratio = models.DecimalField(max_digits = 5, , max_decimal = 3, default="", editable = False)


