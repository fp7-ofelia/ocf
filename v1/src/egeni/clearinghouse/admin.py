from egeni.clearinghouse.models import *
from django.contrib import admin

admin.site.register(AggregateManager)

admin.site.register(Slice)

admin.site.register(Node)
admin.site.register(Link)
admin.site.register(Interface)
admin.site.register(FlowSpace)
admin.site.register(DatedMessage)

admin.site.register(UserProfile)
