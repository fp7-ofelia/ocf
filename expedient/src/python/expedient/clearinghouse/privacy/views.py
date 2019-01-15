"""
Created on Jan 15, 2019

@author: CarolinaFernandez
"""

from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseNotAllowed
from django.views.generic import create_update
from django.views.generic.simple import direct_to_template
from models import UserPrivacy

def home(request):
    """
    Show simple template for privacy terms.

    @param request HTTP request
    @return string template for the privacy main page
    """
    return direct_to_template(
        request,
        template="privacy/index.html",
        extra_context = {}
    )

def privacy_get_or_delete(request, user_urn):
    """
    Get the consent of the user w.r.t. the privacy terms.

    @param string User URN
    """
    if request.method == "GET":
        reply = "user_urn: " + str(user_urn)
        try:
            user = UserPrivacy.objects.get(user_urn=user_urn)
            user_consent = "consented" if user.accept else "declined"
            reply += " has " + str(user_consent)
        except:
            reply += " does not exist"
        return HttpResponse(reply, mimetype="text/plain")
    elif request.method == "DELETE":
        return privacy_delete(request, user_urn)
    else:
        return HttpResponseNotAllowed("GET", "DELETE")

def privacy_accept(request, user_urn):
    """
    Approve the privacy terms on behalf of a user.

    @param string User URN
    """
    if request.method == "GET":
        return privacy_update(user_urn, True)
    else:
        return HttpResponseNotAllowed("GET")

def privacy_decline(request, user_urn):
    """
    Decline the privacy terms on behalf of a user.

    @param string User URN
    """
    if request.method == "GET":
        return privacy_update(user_urn, False)
    else:
        return HttpResponseNotAllowed("GET")

def privacy_delete(request, user_urn):
    """
    Delete the entry for a given user in the privacy terms table.

    @param string User URN
    """
    return privacy_remove(user_urn)

def privacy_remove(user_urn):
    """
    Delete the entry for a given user in the privacy terms table.

    @param string User URN
    """
    try:
        user = UserPrivacy.objects.get(user_urn=user_urn)
        user.delete()
    except:
        user = None
        user_urn = "%s already" % user_urn
    return HttpResponse("User with URN=%s deleted" % user_urn)

def privacy_update(user_urn, accept_or_decline):
    """
    Update the entry for a given user in the privacy terms table.

    @param string User URN
    @param bool Accept (true) or decline (false) terms
    """
    # Create or update, as needed
    try:
        user = UserPrivacy.objects.get(user_urn=user_urn)
        # Only update if consent changes
        if user.accept != accept_or_decline:
            user.accept = accept_or_decline
            # TODO Take value from configuration
            user.date_mod = datetime.now() + timedelta(days=180)
            user.save()
    except Exception as e:
        user = UserPrivacy.objects.create(user_urn=user_urn,
            accept=accept_or_decline, date_mod=datetime.now())
    user_consent = "consent" if accept_or_decline else "decline"
    return HttpResponse("User with URN=%s updated to %s the terms" % (user_urn, user_consent))

