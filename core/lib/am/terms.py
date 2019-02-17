from ambase.config.terms import TERMS_CONDITIONS_PRIV_URL
import json
import re
import urllib2

class TermsAndConditions(object):

    @staticmethod
    def get_user_conformity(credentials):
        # Enforce user to accept the terms and conditions to operate in the testbed
        owner_urn_regex = "\<owner_urn\>(.*)<\/owner_urn\>"
        m = re.search(owner_urn_regex, str(credentials))
        try:
            user_urn = m.group(1)
            # Contact the T&C URL
            tc_user_url_get = "%s%s" % (TERMS_CONDITIONS_PRIV_URL, user_urn)
            response = urllib2.urlopen(tc_user_url_get)
            reply = response.read()
            if reply is not None:
                user_testbed_access = json.loads(reply)
                user_testbed_access = user_testbed_access.get("testbed_access", False)
            response.close()
        except Exception as e:
            print(e)
            user_urn = ""
            user_testbed_access = False
        if not user_testbed_access:
            raise Exception("TermsNotAccepted")
