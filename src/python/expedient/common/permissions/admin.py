'''
Created on May 28, 2010

@author: jnaous
'''
import models
from django.contrib import admin

admin.site.register(models.ExpedientPermission)
admin.site.register(models.ControlledContentType)
admin.site.register(models.ControlledModel)
admin.site.register(models.PermissionInfo)
admin.site.register(models.PermissionUserModel)
