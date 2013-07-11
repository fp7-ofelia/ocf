"""
@author: CarolinaFernandez
"""

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('expedient.clearinghouse.help.views',
    url(r'^', 'home', name="help_home"),
)
