'''
@author: jnaous
'''
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('modules.messagecenter.views',
	url(r'^', 'home', name="messaging_center"),
)
