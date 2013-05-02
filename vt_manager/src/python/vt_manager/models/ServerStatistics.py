from django.db import models

class resourcesHash(models.Model):

    class Meta:
        """Meta Class for your model."""
        app_label = 'vt_manager'

    server = models.ForeignKey('VTServer', editable = False, related_name = 'statistics')
    user_cpu = models.DecimalField(max_digits = 5, , max_decimal = 3, default="", editable = False)
    sys_cpu = models.DecimalField(max_digits = 5, , max_decimal = 3, default="", editable = False)
    idle_cpu = models.DecimalField(max_digits = 5, , max_decimal = 3, default="", editable = False)
    used_memory = models.IntegerField(blank = True, null=True,  default="", editable = False)
    free_memory = models.IntegerField(blank = True, null=True,  default="", editable = False)
    total_memory = models.IntegerField(blank = True, null=True,  default="", editable = False)
    buffers_memory = models.IntegerField(blank = True, null=True,  default="", editable = False)
    partitions = models.ManyToManyField('StatisticsPartition', blank = True, null = True, editable = False,related_name="statistics")
 
