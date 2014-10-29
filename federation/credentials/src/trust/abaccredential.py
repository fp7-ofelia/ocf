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

from credentials.src.trust.credential import Credential
from credentials.src.trust.credential import DEFAULT_CREDENTIAL_LIFETIME
from credentials.src.trust.credential import append_sub


from StringIO import StringIO
from xml.dom.minidom import Document, parseString
from geniutils.src.faults.faults import CredentialNotVerifiable
import datetime
from dateutil import tz

HAVELXML = False
try:
    from lxml import etree
    HAVELXML = True
except:
    pass

# This module defines a subtype of sfa.trust,credential.Credential
# called an ABACCredential. An ABAC credential is a signed statement
# asserting a role representing the relationship between a subject and target
# or between a subject and a class of targets (all those satisfying a role).
#
# An ABAC credential is like a normal SFA credential in that it has
# a validated signature block and is checked for expiration. 
# It does not, however, have 'privileges'. Rather it contains a 'head' and
# list of 'tails' of elements, each of which represents a principal and
# role.

# A special case of an ABAC credential is a speaks_for credential. Such
# a credential is simply an ABAC credential in form, but has a single 
# tail and fixed role 'speaks_for'. In ABAC notation, it asserts
# AGENT.speaks_for(AGENT)<-CLIENT, or "AGENT asserts that CLIENT may speak
# for AGENT". The AGENT in this case is the head and the CLIENT is the
# tail and 'speaks_for_AGENT' is the role on the head. These speaks-for
# Credentials are used to allow a tool to 'speak as' itself but be recognized
# as speaking for an individual and be authorized to the rights of that
# individual and not to the rights of the tool itself.

# For more detail on the semantics and syntax and expected usage patterns
# of ABAC credentials, see http://groups.geni.net/geni/wiki/TIEDABACCredential.


# An ABAC element contains a principal (keyid and optional mnemonic)
# and optional role and linking_role element
class ABACElement:
    def __init__(self, principal_keyid, principal_mnemonic=None, \
                     role=None, linking_role=None):
        self._principal_keyid = principal_keyid
        self._principal_mnemonic = principal_mnemonic
        self._role = role
        self._linking_role = linking_role

    def get_principal_keyid(self): return self._principal_keyid
    def get_principal_mnemonic(self): return self._principal_mnemonic
    def get_role(self): return self._role
    def get_linking_role(self): return self._linking_role

    def __str__(self):
        ret = self._principal_keyid
        if self._principal_mnemonic:
            ret = "%s (%s)" % (self._principal_mnemonic, self._principal_keyid)
        if self._linking_role:
            ret += ".%s" % self._linking_role
        if self._role:
            ret += ".%s" % self._role
        return ret

# Subclass of Credential for handling ABAC credentials
# They have a different cred_type (geni_abac vs. geni_sfa)
# and they have a head and tail and role (as opposed to privileges)
class ABACCredential(Credential):

    ABAC_CREDENTIAL_TYPE = 'geni_abac'

    def __init__(self, create=False, subject=None, 
                 string=None, filename=None):
        self.head = None # An ABACElemenet
        self.tails = [] # List of ABACElements
        super(ABACCredential, self).__init__(create=create, 
                                             subject=subject, 
                                             string=string, 
                                             filename=filename)
        self.cred_type = ABACCredential.ABAC_CREDENTIAL_TYPE

    def get_head(self) : 
        if not self.head: 
            self.decode()
        return self.head

    def get_tails(self) : 
        if len(self.tails) == 0:
            self.decode()
        return self.tails

    def decode(self):
        super(ABACCredential, self).decode()
        # Pull out the ABAC-specific info
        doc = parseString(self.xml)
        rt0s = doc.getElementsByTagName('rt0')
        if len(rt0s) != 1:
            raise CredentialNotVerifiable("ABAC credential had no rt0 element")
        rt0_root = rt0s[0]
        heads = self._get_abac_elements(rt0_root, 'head')
        if len(heads) != 1:
            raise CredentialNotVerifiable("ABAC credential should have exactly 1 head element, had %d" % len(heads))

        self.head = heads[0]
        self.tails = self._get_abac_elements(rt0_root, 'tail')

    def _get_abac_elements(self, root, label):
        abac_elements = []
        elements = root.getElementsByTagName(label)
        for elt in elements:
            keyids = elt.getElementsByTagName('keyid')
            if len(keyids) != 1:
                raise CredentialNotVerifiable("ABAC credential element '%s' should have exactly 1 keyid, had %d." % (label, len(keyids)))
            keyid_elt = keyids[0]
            keyid = keyid_elt.childNodes[0].nodeValue.strip()

            mnemonic = None
            mnemonic_elts = elt.getElementsByTagName('mnemonic')
            if len(mnemonic_elts) > 0:
                mnemonic = mnemonic_elts[0].childNodes[0].nodeValue.strip()

            role = None
            role_elts = elt.getElementsByTagName('role')
            if len(role_elts) > 0:
                role = role_elts[0].childNodes[0].nodeValue.strip()

            linking_role = None
            linking_role_elts = elt.getElementsByTagName('linking_role')
            if len(linking_role_elts) > 0:
                linking_role = linking_role_elts[0].childNodes[0].nodeValue.strip()

            abac_element = ABACElement(keyid, mnemonic, role, linking_role)
            abac_elements.append(abac_element)

        return abac_elements

    def dump_string(self, dump_parents=False, show_xml=False):
        result = "ABAC Credential\n"
        filename=self.get_filename()
        if filename: result += "Filename %s\n"%filename
        if self.expiration:
            result +=  "\texpiration: %s \n" % self.expiration.isoformat()

        result += "\tHead: %s\n" % self.get_head() 
        for tail in self.get_tails():
            result += "\tTail: %s\n" % tail
        if self.get_signature():
            result += "  gidIssuer:\n"
            result += self.get_signature().get_issuer_gid().dump_string(8, dump_parents)
        if show_xml and HAVELXML:
            try:
                tree = etree.parse(StringIO(self.xml))
                aside = etree.tostring(tree, pretty_print=True)
                result += "\nXML:\n\n"
                result += aside
                result += "\nEnd XML\n"
            except:
                import traceback
                print "exc. Credential.dump_string / XML"
                traceback.print_exc()
        return result

    # sounds like this should be __repr__ instead ??
    # Produce the ABAC assertion. Something like [ABAC cred: Me.role<-You] or similar
    def get_summary_tostring(self):
        result = "[ABAC cred: " + str(self.get_head())
        for tail in self.get_tails():
            result += "<-%s" % str(tail)
        result += "]"
        return result

    def createABACElement(self, doc, tagName, abacObj):
        kid = abacObj.get_principal_keyid()
        mnem = abacObj.get_principal_mnemonic() # may be None
        role = abacObj.get_role() # may be None
        link = abacObj.get_linking_role() # may be None
        ele = doc.createElement(tagName)
        prin = doc.createElement('ABACprincipal')
        ele.appendChild(prin)
        append_sub(doc, prin, "keyid", kid)
        if mnem:
            append_sub(doc, prin, "mnemonic", mnem)
        if role:
            append_sub(doc, ele, "role", role)
        if link:
            append_sub(doc, ele, "linking_role", link)
        return ele

    ##
    # Encode the attributes of the credential into an XML string
    # This should be done immediately before signing the credential.
    # WARNING:
    # In general, a signed credential obtained externally should
    # not be changed else the signature is no longer valid.  So, once
    # you have loaded an existing signed credential, do not call encode() or sign() on it.

    def encode(self):
        # Create the XML document
        doc = Document()
        signed_cred = doc.createElement("signed-credential")

# Declare namespaces
# Note that credential/policy.xsd are really the PG schemas
# in a PL namespace.
# Note that delegation of credentials between the 2 only really works
# cause those schemas are identical.
# Also note these PG schemas talk about PG tickets and CM policies.
        signed_cred.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        signed_cred.setAttribute("xsi:noNamespaceSchemaLocation", "http://www.geni.net/resources/credential/2/credential.xsd")
        signed_cred.setAttribute("xsi:schemaLocation", "http://www.planet-lab.org/resources/sfa/ext/policy/1 http://www.planet-lab.org/resources/sfa/ext/policy/1/policy.xsd")

# PG says for those last 2:
#        signed_cred.setAttribute("xsi:noNamespaceSchemaLocation", "http://www.protogeni.net/resources/credential/credential.xsd")
#        signed_cred.setAttribute("xsi:schemaLocation", "http://www.protogeni.net/resources/credential/ext/policy/1 http://www.protogeni.net/resources/credential/ext/policy/1/policy.xsd")

        doc.appendChild(signed_cred)

        # Fill in the <credential> bit
        cred = doc.createElement("credential")
        cred.setAttribute("xml:id", self.get_refid())
        signed_cred.appendChild(cred)
        append_sub(doc, cred, "type", "abac")

        # Stub fields
        append_sub(doc, cred, "serial", "8")
        append_sub(doc, cred, "owner_gid", '')
        append_sub(doc, cred, "owner_urn", '')
        append_sub(doc, cred, "target_gid", '')
        append_sub(doc, cred, "target_urn", '')
        append_sub(doc, cred, "uuid", "")

        if not self.expiration:
            self.set_expiration(datetime.datetime.utcnow() + datetime.timedelta(seconds=DEFAULT_CREDENTIAL_LIFETIME))
        self.expiration = self.expiration.replace(microsecond=0)
        if self.expiration.tzinfo is not None and self.expiration.tzinfo.utcoffset(self.expiration) is not None:
            # TZ aware. Make sure it is UTC
            self.expiration = self.expiration.astimezone(tz.tzutc())
        append_sub(doc, cred, "expires", self.expiration.strftime('%Y-%m-%dT%H:%M:%SZ')) # RFC3339

        abac = doc.createElement("abac")
        rt0 = doc.createElement("rt0")
        abac.appendChild(rt0)
        cred.appendChild(abac)
        append_sub(doc, rt0, "version", "1.1")
        head = self.createABACElement(doc, "head", self.get_head())
        rt0.appendChild(head)
        for tail in self.get_tails():
            tailEle = self.createABACElement(doc, "tail", tail)
            rt0.appendChild(tailEle)

        # Create the <signatures> tag
        signatures = doc.createElement("signatures")
        signed_cred.appendChild(signatures)

        # Get the finished product
        self.xml = doc.toxml("utf-8")
