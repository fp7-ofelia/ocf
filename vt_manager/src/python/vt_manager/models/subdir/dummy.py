from django.db import models

class dummy(models.Model):
    """dummy"""

    class Meta:
        """Meta Class for your model."""
        app_label = 'vt_manager'

    dummy = models.CharField(max_length = 1024, default="")
