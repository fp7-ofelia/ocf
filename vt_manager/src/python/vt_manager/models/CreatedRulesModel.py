import os
import sys
import time
from django.db import models


class CreatedRuledTables(models.Model):
        class Meta: 
                """Machine exportable class"""
                app_label = 'vt_manager'
                db_table = 'policyEngine_CreatedRuledTables'

        name = models.CharField(max_length = 512, default="") # name of the RuleTables availables
        uuid = models.CharField(max_length = 512, default="") # uuid of the RuleTables availables
