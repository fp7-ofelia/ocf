# admin file for flowspace - to be used in debuging
from OM.flowspace.models import OptedInFlowSpace
from django.contrib import admin

class OptedInFlowSpaceAdmin(admin.ModelAdmin):
    pass
    #fields = ('user', 'in_net_admin', 'max_priority_level','supervisor')

admin.site.register(OptedInFlowSpace, OptedInFlowSpaceAdmin)
