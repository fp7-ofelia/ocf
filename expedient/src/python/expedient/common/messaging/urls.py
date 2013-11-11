'''
Created on Apr 27, 2010

@author: jnaous
'''

from django.conf.urls.defaults import patterns, url
from django.conf import settings

urlpatterns = patterns('expedient.common.messaging.views',
    url(r'^list/$', 'list_msgs', {'number': settings.NUM_LATEST_MSGS}, name='messaging_latest'),
    url(r'^list/all/$', 'list_msgs', name='messaging_all'),
    url(r'^list/(?P<number>\d+)/$', 'list_msgs', name='messaging_subset'),
    url(r'^create/$', 'create', name="messaging_create"),
)

urlpatterns += patterns('django.views.generic',
    url(r'^created/$',
        'simple.direct_to_template',
        {'template': "expedient/common/messaging/created.html"},
        name="messaging_created"),
)
