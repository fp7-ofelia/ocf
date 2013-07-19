"""
@author: CarolinaFernandez
"""

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('modules.help.views',
    url(r'^', 'home', name="help_home"),
)
