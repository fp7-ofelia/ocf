'''
Created on Apr 28, 2010

@author: jnaous
'''
from models import *
from django.contrib import admin

admin.site.register(Aggregate)
admin.site.register(AggregateAdminInfo)
admin.site.register(AggregateProjectInfo)
admin.site.register(AggregateSliceInfo)
admin.site.register(AggregateUserInfo)
