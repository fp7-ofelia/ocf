#----------------------------------------------------------------------
# Copyright (c) 2014 Raytheon BBN Technologies
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and/or hardware specification (the "Work") to
# deal in the Work without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Work, and to permit persons to whom the Work
# is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Work.
#
# THE WORK IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE WORK OR THE USE OR OTHER DEALINGS
# IN THE WORK.
#----------------------------------------------------------------------

from __future__ import absolute_import

from credentials.src.trustgcf.credential import Credential
from credentials.src.trustgcf.abac_credential import ABACCredential

import json
import re

# Factory for creating credentials of different sorts by type.
# Specifically, this factory can create standard SFA credentials
# and ABAC credentials from XML strings based on their identifying content

class CredentialFactory:

    UNKNOWN_CREDENTIAL_TYPE = 'geni_unknown'

    # Static Credential class method to determine the type of a credential
    # string depending on its contents
    @staticmethod
    def getType(credString):
        credString_nowhitespace = re.sub('\s', '', credString)
        if credString_nowhitespace.find('<type>abac</type>') > -1:
            return ABACCredential.ABAC_CREDENTIAL_TYPE
        elif credString_nowhitespace.find('<type>privilege</type>') > -1:
            return Credential.SFA_CREDENTIAL_TYPE
        else:
            st = credString_nowhitespace.find('<type>')
            end = credString_nowhitespace.find('</type>', st)
            return credString_nowhitespace[st + len('<type>'):end]
#            return CredentialFactory.UNKNOWN_CREDENTIAL_TYPE

    # Static Credential class method to create the appropriate credential
    # (SFA or ABAC) depending on its type
    @staticmethod
    def createCred(credString=None, credFile=None):
        if not credString and not credFile:
            raise Exception("CredentialFactory.createCred called with no argument")
        if credFile:
            try:
                credString = open(credFile).read()
            except Exception, e:
                return None

        # Try to treat the file as JSON, getting the cred_type from the struct
        try:
            credO = json.loads(credString, encoding='ascii')
            if credO.has_key('geni_value') and credO.has_key('geni_type'):
                cred_type = credO['geni_type']
                credString = credO['geni_value']
        except Exception, e:
            # It wasn't a struct. So the credString is XML. Pull the type directly from the string
            cred_type = CredentialFactory.getType(credString)

        if cred_type == Credential.SFA_CREDENTIAL_TYPE:
            try:
                cred = Credential(string=credString)
                return cred
            except Exception, e:
                if credFile:
                    msg = "credString started: %s" % credString[:50]
                    raise Exception("%s not a parsable SFA credential: %s. " % (credFile, e) + msg)
                else:
                    raise Exception("SFA Credential not parsable: %s. Cred start: %s..." % (e, credString[:50]))

        elif cred_type == ABACCredential.ABAC_CREDENTIAL_TYPE:
            try:
                cred = ABACCredential(string=credString)
                return cred
            except Exception, e:
                if credFile:
                    raise Exception("%s not a parsable ABAC credential: %s" % (credFile, e))
                else:
                    raise Exception("ABAC Credential not parsable: %s. Cred start: %s..." % (e, credString[:50]))
        else:
            raise Exception("Unknown credential type '%s'" % cred_type)

if __name__ == "__main__":
    c2 = open('/tmp/sfa.xml').read()
    cred1 = CredentialFactory.createCred(credFile='/tmp/cred.xml')
    cred2 = CredentialFactory.createCred(credString=c2)

    print "C1 = %s" % cred1
    print "C2 = %s" % cred2
    c1s = cred1.dump_string()
    print "C1 = %s" % c1s
#    print "C2 = %s" % cred2.dump_string()
