from django.conf.urls.defaults import *
from demo.views import *

urlpatterns = patterns( '',
    url( r'^$', index, name = 'demo_index' ),
	url( r'^users/$', ajax_user_search, name = 'demo_user_search' ),
)
