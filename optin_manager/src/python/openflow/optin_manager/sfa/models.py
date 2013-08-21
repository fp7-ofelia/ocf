from django.db import models
from datetime import datetime
import uuid

class ExpiringComponents(models.Model):
    """Class to relate slivers to an expiration date"""

    slice = models.CharField(max_length = 512, default="")
    authority = models.CharField(max_length = 512, default="")
    expires = models.CharField(max_length = 512, default="") #Better fields?

    def extend_expiration(self,new_expiration):
        self.expires = new_expiration
        self.save()
