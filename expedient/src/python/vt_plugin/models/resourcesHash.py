from django.db import models

class resourcesHash(models.Model):

    class Meta:
        """Meta Class for your model."""
        app_label = 'vt_plugin'

    #hashValue = models.IntegerField()
    hashValue = models.CharField(max_length = 1024, default="")
    #serverUUID = models.CharField(max_length = 1024, default="")
    vtamID = models.IntegerField(default="-1")
    projectUUID = models.CharField(max_length = 1024, default="")
    sliceUUID = models.CharField(max_length = 1024, default="")
