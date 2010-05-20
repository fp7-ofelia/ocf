'''
@author: jnaous
'''
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('expedient.clearinghouse.project.views',
    url(r'^(?P<proj_id>\d+)/detail/$', 'detail', name='project_detail'),
    url(r'^(?P<proj_id>\d+)/edit/$', 'edit', name='project_edit'),
    url(r'^(?P<proj_id>\d+)/saved/$', 'saved', name='project_saved'),
    url(r'^(?P<proj_id>\d+)/delete/$', 'delete', name="project_delete"),
)
