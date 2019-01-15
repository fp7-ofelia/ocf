"""
@author: CarolinaFernandez
"""

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns("expedient.clearinghouse.privacy.views",
    url(r"^$", "home", name="privacy_home"),
    url(r"^(?P<user_urn>urn:publicid:IDN\+([\w|\d|\.]+)\+user\+([\w\d]+))$", "privacy_get_or_delete", name="privacy_get_or_delete"),
    url(r"^(?P<user_urn>urn:publicid:IDN\+([\w|\d|\.]+)\+user\+([\w\d]+))/accept/$", "privacy_accept", name="privacy_accept"),
    url(r"^(?P<user_urn>urn:publicid:IDN\+([\w|\d|\.]+)\+user\+([\w\d]+))/decline/$", "privacy_decline", name="privacy_decline"),
    url(r"^(?P<user_urn>urn:publicid:IDN\+([\w|\d|\.]+)\+user\+([\w\d]+))/delete/$", "privacy_delete", name="privacy_delete"),
)
