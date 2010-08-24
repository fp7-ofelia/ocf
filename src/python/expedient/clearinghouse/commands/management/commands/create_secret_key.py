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
        print "Generating new key in secret_key.py..."
        key = ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
        f = open(os.path.join(settings.PROJ_DIR, "secret_key.py"), mode="w")
        f.write("SECRET_KEY = '%s'\n" % key)
        f.close()
        print "Done."
        