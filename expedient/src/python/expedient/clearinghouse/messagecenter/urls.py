'''
@author: jnaous
'''
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('expedient.clearinghouse.messagecenter.views',
    url(r'^', 'home', name="messaging_center"),
)
