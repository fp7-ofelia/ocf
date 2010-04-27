'''
Created on Apr 15, 2010

@author: jnaous
'''
from django.contrib.auth.models import User
from clearinghouse.users.models import UserProfile

add_rule(
    model=User,
    fields=["email"],
    readers=lambda user: User.objects.filter(project__in=user.project_set).all(),
    writers=lambda user: [user],
)

add_rule(
    model=User,
    fields=["username", "first_name", "last_name"],
    readers=lambda user: User.objects.all(),
    writers=lambda user: [user],
)

add_rule(
    model=User,
    fields=["last_login", "date_joined"],
    readers=lambda user: [user],
    writers=lambda user: [],
)

add_rule(
    model=User,
    fields=["password"],
    readers=lambda user: [],
    writers=lambda user: [user],
)

add_rule(
    model=User,
    fields=["is_staff", "is_active", "is_superuser"],
    readers=lambda user: [],
    writers=lambda user: [],
)

add_rule(
    model=UserProfile,
    fields=["affiliation"],
    readers=lambda profile: User.objects.all(),
    writers=lambda profile: [profile.user],
)

add_rule(
    model=UserProfile,
    fields=["is_clearinghouse_admin"],
    readers=lambda profile: User.objects.all(),
    writers=lambda profile: User.objects.filter(is_clearinghouse_admin=True),
)

