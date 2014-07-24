'''Command to link static content to settings.STATIC_DOC_ROOT

Created on Aug 24, 2010

@author: jnaous
'''
from django.core.management.base import NoArgsCommand
from django.conf import settings
import pkg_resources
import os

class Command(NoArgsCommand):
    help = "Link static content from package to %s" % settings.STATIC_DOC_ROOT

    def handle_noargs(self, **options):
        pkg_resources.ensure_directory(settings.MEDIA_ROOT)
        pkg_resources.ensure_directory(
            os.path.join(settings.MEDIA_ROOT, settings.AGGREGATE_LOGOS_DIR))
        
        media_dir = os.path.join(
            settings.SRC_DIR, "static", "expedient", "clearinghouse", "media")
        
        for d in "css", "img", "js":
            path = os.path.join(media_dir, d)
            target = os.path.join(settings.MEDIA_ROOT, d)
            if not os.access(target, os.F_OK):
                os.symlink(path, target)
                
        print "Created media directory and symlinks in %s" \
            % settings.MEDIA_ROOT
        
