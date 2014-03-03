from django.db import models

class resourcesHash(models.Model):

    class Meta:
        """Meta Class for your model."""
        app_label = 'vt_manager'

    #hashValue = models.IntegerField()
    hashValue = models.CharField(max_length = 1024, default="")
    #serverUUID = models.CharField(max_length = 1024, default="")
    projectUUID = models.CharField(max_length = 1024, default="")
    sliceUUID = models.CharField(max_length = 1024, default="")
