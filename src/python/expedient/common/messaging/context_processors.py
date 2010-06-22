'''
Created on Jun 19, 2010

@author: jnaous
'''
from models import DatedMessage
from django.conf import settings
def messaging(request):
    if request.user.is_authenticated():
        qs = DatedMessage.objects.get_messages_for_user(
            request.user).order_by('-datetime')[:settings.NUM_CONTEXT_MSGS]
        l = list(qs)
    else:
        l = []
    return {"messages": l}
