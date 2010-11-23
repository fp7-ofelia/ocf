'''
Created on Apr 28, 2010

@author: jnaous
'''
from models import *
from django.contrib import admin

#admin.site.register(OpenFlowAdminInfo)
admin.site.register(OpenFlowAggregate)
admin.site.register(OpenFlowConnection)
admin.site.register(OpenFlowInterface)
#admin.site.register(OpenFlowInterfaceSliver)
#admin.site.register(OpenFlowProjectInfo)
admin.site.register(OpenFlowSliceInfo)
admin.site.register(OpenFlowSwitch)
#admin.site.register(OpenFlowSwitchSliver)
#admin.site.register(OpenFlowUserInfo)
admin.site.register(FlowSpaceRule)
