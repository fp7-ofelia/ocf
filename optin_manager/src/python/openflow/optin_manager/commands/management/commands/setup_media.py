'''Command to link static content to settings.STATIC_DOC_ROOT

Created on Sep 4, 2010

@author: Peyman Kazemian
'''
from django.core.management.base import NoArgsCommand
from django.conf import settings
import pkg_resources
import os

class Command(NoArgsCommand):
    help = "Link static content from package to %s" % settings.STATIC_DOC_ROOT

    def handle_noargs(self, **options):
        pkg_resources.ensure_directory(settings.MEDIA_ROOT)
        
        media_dir = os.path.join(
            settings.SRC_DIR, "static", "openflow", "optin_manager", "media")
        
        for root, dirs, files in os.walk(media_dir):
            for name in files:
                file = os.path.join(media_dir, name)
                target = os.path.join(settings.MEDIA_ROOT,name)
                if not os.access(target, os.F_OK):
                    os.symlink(file, target)
                
        print "Created media directory and symlinks in %s" \
            % settings.MEDIA_ROOT
        