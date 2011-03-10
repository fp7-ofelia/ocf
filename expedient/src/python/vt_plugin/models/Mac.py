from django.db import models
from django.contrib import auth

class Mac(models.Model):
    """MAC"""

    class Meta:
        """Meta Class for your model."""
        app_label = 'vt_plugin'

    projectID = models.CharField(max_length = 1024, default="")
    sliceID = models.CharField(max_length = 1024, default="")
    mac = models.CharField(max_length = 17, default="")
    vmID = models.CharField(max_length = 512, default="")
    isMgmt = models.BooleanField()
    ifaceName = models.CharField(max_length = 512, default="")
