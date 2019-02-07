"""
Created on Jan 15, 2018

@author: CarolinaFernandez
"""

from django.db import models

class UserPrivacy(models.Model):
    """
    Status of the consent of any given user of the Terms and Conditions.
    """

    user_urn = models.CharField(primary_key=True, max_length=255, default="")
    accept = models.BooleanField(default=False)
    date_mod = models.DateTimeField(auto_now=False, auto_now_add=False)

    def __unicode__(self):
        try:
            return "User=%s accepts=%s on date=Profile for %s" % (user_urn, accept, date_mod.strftime('%Y-%m-%d %H:%M:%S'))
        except:
            return None

