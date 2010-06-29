# admin file for flowspace - to be used in debuging
from models import *
from django.contrib import admin

admin.site.register(MatchStruct)
admin.site.register(UserOpts)
admin.site.register(OptsFlowSpace)

admin.site.register(Experiment)
admin.site.register(ExperimentFLowSpace)

admin.site.register(AdminFlowSpace)
admin.site.register(UserFlowSpace)
