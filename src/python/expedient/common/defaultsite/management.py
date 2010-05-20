'''
Create the default Site object.

@author: oppianmatt, jnaous
'''

import settings
from django.contrib.sites import models as site_app
from django.contrib.sites.models import Site
from django.db.models import signals

def create_default_site(sender, app, created_models, verbosity, interactive, **kwargs):
    # first check for existing site id
    try:
        site = Site.objects.get(id=settings.SITE_ID)
        # delete it if it exists
        site.delete()
    except:
        # site doesn't exist
        pass

    s = Site(id=settings.SITE_ID, domain=settings.SITE_DOMAIN, name=settings.SITE_NAME)
    if verbosity >= 2:
        print "Site object:"
        print s
    s.save()
    # clear the cache
    Site.objects.clear_cache()

signals.post_syncdb.connect(create_default_site, sender=site_app)
