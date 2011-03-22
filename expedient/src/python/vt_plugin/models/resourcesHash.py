from django.db import models

class resourcesHash(models.Model):

    class Meta:
        """Meta Class for your model."""
        app_label = 'vt_plugin'

    hashValue = models.IntegerField()
    serverUUID = models.CharField(max_length = 1024, default="")
    projectUUID = models.CharField(max_length = 1024, default="")
    sliceUUID = models.CharField(max_length = 1024, default="")
