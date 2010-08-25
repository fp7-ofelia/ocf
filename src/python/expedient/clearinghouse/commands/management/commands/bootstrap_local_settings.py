'''Command to bootstrap local settings with None values.

Created on Aug 24, 2010

@author: jnaous
'''
from optparse import make_option
import pkg_resources
import os
from django.core.management.base import NoArgsCommand
from django.conf import settings

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

    def handle_noargs(self, **options):
        conf_dir = os.path.abspath(options.get('path', settings.CONF_DIR))
        loc = os.path.join(conf_dir, "localsettings.py")
        pkg_resources.ensure_directory(loc)
        if os.access(loc, os.F_OK):
            print "ERROR: Found localsettings already. "\
                "Cowardly refusing to overwrite."
            return
        print "Creating skeleton localsettings.py file. in %s" % conf_dir
        f = open(loc, mode="w")
        # write the conf dir location
        f.write("CONF_DIR = '%s'\n" % conf_dir)
        for item in settings.REQUIRED_SETTINGS:
            for var in item[1]:
                f.write("%s = None\n" % var)
        f.close()
        print "Done."
        