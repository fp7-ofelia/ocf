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
import re

def home(request):
    """
    Show simple template for privacy terms.

    @param request HTTP request
    @return string template for the privacy main page
    """
    ssl_client_s_dn = request.__dict__.get("environ", {}).get("SSL_CLIENT_S_DN", "")
    ssl_client_dn_fields = parse_cert_dn(ssl_client_s_dn)
    cert_dn_fields_user = ssl_client_dn_fields.get("email", "").split("@")
    if len(cert_dn_fields_user) >= 2:
        user_urn = "urn:publicid:IDN+%s+user+%s" % (cert_dn_fields_user[1], cert_dn_fields_user[0])
    else:
        user_urn = "urn:publicid:IDN+%s+user+%s" % (ssl_client_dn_fields.get("email", ""), ssl_client_dn_fields.get("CN", ""))
    return direct_to_template(
        request,
        template="privacy/index.html",
        extra_context = {
            "user_urn": user_urn,
            "until_date": get_until_date(),
        }
    )

def parse_cert_dn(cert_dn):
    cert_dn_regex = "\/C=(.*)\/ST=(.*)\/O=(.*)\/OU=(.*)\/CN=(.*)\/emailAddress=(.*)"
    cert_dn_fields = {}
    m = re.search(cert_dn_regex, cert_dn)
    try:
        cert_dn_fields["C"] = m.group(1)
        cert_dn_fields["ST"] = m.group(2)
        cert_dn_fields["O"] = m.group(3)
        cert_dn_fields["OU"] = m.group(4)
        cert_dn_fields["CN"] = m.group(5)
        cert_dn_fields["email"] = m.group(6)
    except:
        pass
    return cert_dn_fields

def get_until_date(time_delta=180):
    return datetime.now() + timedelta(days=180)

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
            user.date_mod = get_until_date()
            user.save()
    except Exception as e:
        user = UserPrivacy.objects.create(user_urn=user_urn,
            accept=accept_or_decline, date_mod=get_until_date())
    user_consent = "consent" if accept_or_decline else "decline"
    return HttpResponse("User with URN=%s updated to %s the terms" % (user_urn, user_consent), status=204)

