'''Command to create a secret_key.py file and a new secret key to it.

Created on Aug 23, 2010

@author: jnaous
'''
from random import choice
from django.core.management.base import NoArgsCommand
from django.conf import settings
import os.path

class Command(NoArgsCommand):
    help = "Generate a new secret key and write it in secret_key.py"

    def handle_noargs(self, **options):
        filepath = os.path.join(settings.CONF_DIR, "secret_key.py")
        print "Generating new key in %s..." % filepath
        key = ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for _ in range(50)])
        f = open(filepath, mode="w")
        f.write("SECRET_KEY = '%s'\n" % key)
        f.close()
        print "Done."
        