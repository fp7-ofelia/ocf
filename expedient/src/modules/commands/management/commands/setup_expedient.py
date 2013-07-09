'''Calls all the management commands needed to set up Expedient after
installing an egg or getting source from git and writing local settings.

Created on Aug 24, 2010

@author: jnaous
'''
from django.core.management.base import NoArgsCommand
from django.core.management import call_command

class Command(NoArgsCommand):
    help = "Calls all the management commands needed to set up " \
        "Expedient after installing an egg or getting source from git " \
        "and writing local settings. You need to already have localsettings "\
        "in your PYTHONPATH."

    def handle_noargs(self, **options):
        call_command("create_secret_key")
        call_command("install_cert_makefile")
        call_command("setup_media")
        