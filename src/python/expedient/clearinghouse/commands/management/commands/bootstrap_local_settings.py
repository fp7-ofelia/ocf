'''Command to bootstrap local settings with None values.

Created on Aug 24, 2010

@author: jnaous
'''
from optparse import make_option
import pkg_resources
import os
from django.core.management.base import NoArgsCommand
from django.conf import settings
from expedient.clearinghouse.commands.utils import bootstrap_local_settings

class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option(
            '--path', action='store', dest='path',
            default=settings.CONF_DIR,
            help='Specifies the location where local settings should ' \
                'be installed. This location should be added to your ' \
                'PYTHONPATH. Defaults to %s' \
                % os.path.abspath(settings.CONF_DIR),
            ),
    )
    help = "Bootstrap a localsettings.py file"
    requires_model_validation = False
    
    def handle_noargs(self, **options):
        conf_dir = os.path.abspath(options.get('path', settings.CONF_DIR))
        bootstrap_local_settings(conf_dir=conf_dir)
        