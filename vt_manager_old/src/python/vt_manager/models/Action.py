from django.db import models
#from django.db.models import SET_NULL
from datetime import datetime
from vt_manager.models.faults import *
from vt_manager.models import VM

class Action(models.Model):
    """Class to store actions"""

    class Meta:
        """Machine exportable class"""
        app_label = 'vt_manager'
    
    hyperaction = models.CharField(max_length = 16, default="")
    type = models.CharField(max_length = 16, default="")
    uuid = models.CharField(max_length = 512, default="")
    callBackUrl = models.URLField()
    status = models.CharField(max_length = 16, default="")
    description = models.CharField(max_length = 2048, default="", blank =True, null =True)
    vm = models.ForeignKey('VM', blank = True, null = True)
    

