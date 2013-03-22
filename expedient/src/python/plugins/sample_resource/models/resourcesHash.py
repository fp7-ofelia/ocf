from django.db import models

class resourcesHash(models.Model):

    class Meta:
        """Meta Class for your model."""
        app_label = 'sample_resource'

    hashValue = models.CharField(max_length = 1024, default="")
    sampleresource_am_id = models.IntegerField(default="-1")
    project_uuid = models.CharField(max_length = 1024, default="")
    slice_uuid = models.CharField(max_length = 1024, default="")

