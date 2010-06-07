'''
Created on Jun 6, 2010

@author: jnaous
'''
from django.conf.urls.defaults import patterns, url
from expedient.common.permissions.utils import CONTROLLED_CLASS_URL_NAME,\
    DEFAULT_CONTROLLED_CLASS_PERMISSIONS

urls = [url(
    r"^%s/%s/%d/" % (ContentType.objects.get_for_model(ContentType).id,perm)+\
    r"(?P<target_id>\d+)/(?P<user_ct_id>\d+)/(?P<user_id>\d+)/$",
    "reraise_class_permission_denied",
    name="%s-%s" % (CONTROLLED_CLASS_URL_NAME, perm),
) for perm in DEFAULT_CONTROLLED_CLASS_PERMISSIONS]

urlpatterns = patterns("expedient.common.permissions.views",
    *urls
)
