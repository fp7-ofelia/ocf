from django.db import models
from datetime import datetime
from vt_plugin.models import *

class Action(models.Model):
    """Class to store actions"""

    class Meta:
        """Machine exportable class"""
        app_label = 'vt_plugin'

    hyperaction = models.CharField(max_length = 16, default="")
    type = models.CharField(max_length = 16, default="")
    uuid = models.CharField(max_length = 512, default="")
    callBackUrl = models.URLField()
    status = models.CharField(max_length = 16, default="")
    description = models.CharField(max_length = 512, default="", blank =True, null =True)
    vm = models.ForeignKey('VM', blank = True, null = True)


