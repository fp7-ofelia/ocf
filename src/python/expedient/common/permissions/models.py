'''
Created on May 28, 2010

@author: jnaous
'''
from django.db import models

add_rule(
    "view_user_profile",
    UserProfile,
    dict(user__project__in=lambda s: s.user.project_set.all()),
)

add_rule(
    "can_edit_aggregate",
    Aggregate,
    dict()
)