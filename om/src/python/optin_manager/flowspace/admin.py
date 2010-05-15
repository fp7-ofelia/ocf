# admin file for flowspace - to be used in debuging
from optin_manager.flowspace.models import UserOpts, Experiment, Topology, ExperimentFLowSpace, OptsFlowSpace, AdminFlowSpace, UserFlowSpace
from django.contrib import admin


admin.site.register(UserOpts)
admin.site.register(Experiment)
admin.site.register(Topology)
admin.site.register(ExperimentFLowSpace)
admin.site.register(OptsFlowSpace)
admin.site.register(AdminFlowSpace)
admin.site.register(UserFlowSpace)