"""A command to run the tests specified in settings.TEST_APPS

Created on Aug 22, 2010

@author: jnaous
"""
import logging
from optparse import make_option
from django.core.management.base import NoArgsCommand
from django.core.management import call_command

class Command(NoArgsCommand):
    help = "This command runs the tests that are bundled with Expedient."

    option_list = NoArgsCommand.option_list + (
        make_option(
            '--debug', action='store_true', dest='debug',
            help='Specifies request to use full logging. Otherwise'
                'the tests are run silently.',
        ),
    )

    def handle_noargs(self, **options):
        from django.conf import settings
        print "Running the following tests:"
        for app in settings.TEST_APPS:
            print "    %s" % app
        
        debug = options.get("debug")
        if not debug:
            logging.disable(logging.WARN)
        call_command("test", *settings.TEST_APPS)
        print "Ran the following tests:"
        for app in settings.TEST_APPS:
            print "    %s" % app
        