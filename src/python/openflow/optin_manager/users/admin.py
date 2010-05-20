from openflow.optin_manager.users.models import UserProfile
from django.contrib import admin

class UserProfileAdmin(admin.ModelAdmin):
    pass
    #fields = ('user', 'in_net_admin', 'max_priority_level','supervisor')

admin.site.register(UserProfile, UserProfileAdmin)
