'''Command to create default administrators.
Created on Aug 26, 2010

@author: jnaous
'''

from django.core.management.base import NoArgsCommand
from django.conf import settings
from django.contrib.auth.models import User

class Command(NoArgsCommand):
    help = "Creates the default root user specified by " \
        "settings.ROOT_USERNAME (%s), settings.ROOT_PASSWORD (%s), " \
        "settings.ROOT_EMAIL (%s). See " \
        "the 'defaultsettings.admins' module documentation. If the user " \
        "already exists, the user's password will be reset, and the user " \
        "will be promoted to superuser." % (
            settings.ROOT_USERNAME, settings.ROOT_PASSWORD,
            settings.ROOT_EMAIL)

    def handle_noargs(self, **options):
        try:
            u = User.objects.get(username=settings.ROOT_USERNAME)
        except User.DoesNotExist:
            User.objects.create_superuser(
                settings.ROOT_USERNAME,
                settings.ROOT_EMAIL,
                settings.ROOT_PASSWORD,
            )
            print "Created superuser %s with password %s." % (
                settings.ROOT_USERNAME, settings.ROOT_PASSWORD)
        else:
            u.set_password(settings.ROOT_PASSWORD)
            u.is_superuser = True
            u.is_staff = True
            u.save()
            print "Reset user %s's password to %s and promoted the user " \
                "to superuser." % (
                    settings.ROOT_USERNAME, settings.ROOT_PASSWORD)
