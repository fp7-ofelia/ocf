'''
Created on Apr 28, 2010

@author: jnaous
'''
from clearinghouse.aggregate import models as aggregate_models
from clearinghouse.messaging import models as messaging_models
from clearinghouse.resources import models as resources_models
from clearinghouse.slice import models as slice_models
from clearinghouse.users import models as users_models

from django.contrib import admin

admin.site.register(aggregate_models.Aggregate)

admin.site.register(messaging_models.DatedMessage)

admin.site.register(resources_models.Resource)
admin.site.register(resources_models.Node)
admin.site.register(resources_models.Link)

admin.site.register(slice_models.Slice)

admin.site.register(users_models.UserProfile)
