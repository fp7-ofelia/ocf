"""A command to run the tests specified in settings.TEST_APPS

Created on Sep 4, 2010

@author: Peyman Kazemian
"""
from django.core.management.base import NoArgsCommand
from django.core.management import call_command

class Command(NoArgsCommand):
    help = "This command runs the tests that are bundled with Opt In Manager."

    def handle_noargs(self, **options):
        from django.conf import settings
        print "Running the following tests:"
        for app in settings.TEST_APPS:
            print "    %s" % app
        call_command("test", *settings.TEST_APPS)
        print "Ran the following tests:"
        for app in settings.TEST_APPS:
            print "    %s" % app
        