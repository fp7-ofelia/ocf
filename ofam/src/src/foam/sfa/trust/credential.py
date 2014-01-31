#----------------------------------------------------------------------
# Copyright (c) 2008 Board of Trustees, Princeton University
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
##
# Implements SFA Credentials
#
# Credentials are signed XML files that assign a subject gid privileges to an object gid
##

import os
from types import StringTypes
import datetime
from StringIO import StringIO
from tempfile import mkstemp
from xml.dom.minidom import Document, parseString

HAVELXML = False
try:
    from lxml import etree
    HAVELXML = True
except:
    pass
HAVELXML = False

from xml.parsers.expat import ExpatError

from foam.sfa.util.faults import CredentialNotVerifiable, ChildRightsNotSubsetOfParent
#from foam.sfa.util.foam.sfa.ogging import logger
from foam.sfa.util.sfatime import utcparse
from foam.sfa.trust.credential_legacy import CredentialLegacy
from foam.sfa.trust.rights import Right, Rights, determine_rights
from foam.sfa.trust.gid import GID
from foam.sfa.util.xrn import urn_to_hrn, hrn_authfor_hrn

# 2 weeks, in seconds 
DEFAULT_CREDENTIAL_LIFETIME = 86400 * 31


# TODO:
# . make privs match between PG and PL
# . Need to add support for other types of credentials, e.g. tickets
# . add namespaces to signed-credential element?

signature_template = \
'''
<Signature xml:id="Sig_%s" xmlns="http://www.w3.org/2000/09/xmldsig#">
  <SignedInfo>
    <CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>
    <SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>
    <Reference URI="#%s">
      <Transforms>
        <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature" />
      </Transforms>
      <DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
      <DigestValue></DigestValue>
    </Reference>
  </SignedInfo>
  <SignatureValue />
  <KeyInfo>
    <X509Data>
      <X509SubjectName/>
      <X509IssuerSerial/>
      <X509Certificate/>
    </X509Data>
    <KeyValue />
  </KeyInfo>
</Signature>
'''

# PG formats the template (whitespace) slightly differently.
# Note that they don't include the xmlns in the template, but add it later.
# Otherwise the two are equivalent.
#signature_template_as_in_pg = \
#'''
#<Signature xml:id="Sig_%s" >
# <SignedInfo>
#  <CanonicalizationMethod      Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>
#  <SignatureMethod      Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>
#  <Reference URI="#%s">
#    <Transforms>
#      <Transform         Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature" />
#    </Transforms>
#    <DigestMethod        Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
#    <DigestValue></DigestValue>
#    </Reference>
# </SignedInfo>
# <SignatureValue />
# <KeyInfo>
#  <X509Data >
#   <X509SubjectName/>
#   <X509IssuerSerial/>
#   <X509Certificate/>
#  </X509Data>
#  <KeyValue />
# </KeyInfo>
#</Signature>
#'''

##
# Convert a string into a bool
# used to convert an xsd:boolean to a Python boolean
def str2bool(str):
    if str.lower() in ['true','1']:
        return True
    return False


##
# Utility function to get the text of an XML element

def getTextNode(element, subele):
    sub = element.getElementsByTagName(subele)[0]
    if len(sub.childNodes) > 0:            
        return sub.childNodes[0].nodeValue
    else:
        return None
        
##
# Utility function to set the text of an XML element
# It creates the element, adds the text to it,
# and then appends it to the parent.

def append_sub(doc, parent, element, text):
    ele = doc.createElement(element)
    ele.appendChild(doc.createTextNode(text))
    parent.appendChild(ele)

##
# Signature contains information about an xmlsec1 signature
# for a signed-credential
#

class Signature(object):
   
    def __init__(self, string=None):
        self.refid = None
        self.issuer_gid = None
        self.xml = None
        if string:
            self.xml = string
            self.decode()


    def get_refid(self):
        if not self.refid:
            self.decode()
        return self.refid

    def get_xml(self):
        if not self.xml:
            self.encode()
        return self.xml

    def set_refid(self, id):
        self.refid = id

    def get_issuer_gid(self):
        if not self.gid:
            self.decode()
        return self.gid        

    def set_issuer_gid(self, gid):
        self.gid = gid

    def decode(self):
        try:
            doc = parseString(self.xml)
        except ExpatError,e:
            raise e
        sig = doc.getElementsByTagName("Signature")[0]
        self.set_refid(sig.getAttribute("xml:id").strip("Sig_"))
        keyinfo = sig.getElementsByTagName("X509Data")[0]
        szgid = getTextNode(keyinfo, "X509Certificate")
        szgid = "-----BEGIN CERTIFICATE-----\n%s\n-----END CERTIFICATE-----" % szgid
        self.set_issuer_gid(GID(string=szgid))        
        
    def encode(self):
        self.xml = signature_template % (self.get_refid(), self.get_refid())


##
# A credential provides a caller gid with privileges to an object gid.
# A signed credential is signed by the object's authority.
#
# Credentials are encoded in one of two ways.  The legacy style places
# it in the subjectAltName of an X509 certificate.  The new credentials
# are placed in signed XML.
#
# WARNING:
# In general, a signed credential obtained externally should
# not be changed else the signature is no longer valid.  So, once
# you have loaded an existing signed credential, do not call encode() or sign() on it.

def filter_creds_by_caller(creds, caller_hrn_list):
        """
        Returns a list of creds who's gid caller matches the
        specified caller hrn
        """
        if not isinstance(creds, list): creds = [creds]
        if not isinstance(caller_hrn_list, list): 
            caller_hrn_list = [caller_hrn_list]
        caller_creds = []
        for cred in creds:
            try:
                tmp_cred = Credential(string=cred)
                if tmp_cred.get_gid_caller().get_hrn() in caller_hrn_list:
                    caller_creds.append(cred)
            except: pass
        return caller_creds

class Credential(object):

    ##
    # Create a Credential object
    #
    # @param create If true, create a blank x509 certificate
    # @param subject If subject!=None, create an x509 cert with the subject name
    # @param string If string!=None, load the credential from the string
    # @param filename If filename!=None, load the credential from the file
    # FIXME: create and subject are ignored!
    def __init__(self, create=False, subject=None, string=None, filename=None):
        self.gidCaller = None
        self.gidObject = None
        self.expiration = None
        self.privileges = None
        self.issuer_privkey = None
        self.issuer_gid = None
        self.issuer_pubkey = None
        self.parent = None
        self.signature = None
        self.xml = None
        self.refid = None
        self.legacy = None

        # Check if this is a legacy credential, translate it if so
        if string or filename:
            if string:                
                str = string
            elif filename:
                str = file(filename).read()
                
            if str.strip().startswith("-----"):
                self.legacy = CredentialLegacy(False,string=str)
                self.translate_legacy(str)
            else:
                self.xml = str
                self.decode()

        # Find an xmlsec1 path
        self.xmlsec_path = ''
        paths = ['/usr/bin','/usr/local/bin','/bin','/opt/bin','/opt/local/bin']
        for path in paths:
            if os.path.isfile(path + '/' + 'xmlsec1'):
                self.xmlsec_path = path + '/' + 'xmlsec1'
                break
        if not self.xmlsec_path:
            print "Could not locate binary for xmlsec1 - SFA will be unable to sign stuff !!"

    def get_subject(self):
        if not self.gidObject:
            self.decode()
        return self.gidObject.get_subject()

    # sounds like this should be __repr__ instead ??
    def get_summary_tostring(self):
        if not self.gidObject:
            self.decode()
        obj = self.gidObject.get_printable_subject()
        caller = self.gidCaller.get_printable_subject()
        exp = self.get_expiration()
        # Summarize the rights too? The issuer?
        return "[ Grant %s rights on %s until %s ]" % (caller, obj, exp)

    def get_signature(self):
        if not self.signature:
            self.decode()
        return self.signature

    def set_signature(self, sig):
        self.signature = sig

        
    ##
    # Translate a legacy credential into a new one
    #
    # @param String of the legacy credential

    def translate_legacy(self, str):
        legacy = CredentialLegacy(False,string=str)
        self.gidCaller = legacy.get_gid_caller()
        self.gidObject = legacy.get_gid_object()
        lifetime = legacy.get_lifetime()
        if not lifetime:
            self.set_expiration(datetime.datetime.utcnow() + datetime.timedelta(seconds=DEFAULT_CREDENTIAL_LIFETIME))
        else:
            self.set_expiration(int(lifetime))
        self.lifeTime = legacy.get_lifetime()
        self.set_privileges(legacy.get_privileges())
        self.get_privileges().delegate_all_privileges(legacy.get_delegate())

    ##
    # Need the issuer's private key and name
    # @param key Keypair object containing the private key of the issuer
    # @param gid GID of the issuing authority

    def set_issuer_keys(self, privkey, gid):
        self.issuer_privkey = privkey
        self.issuer_gid = gid


    ##
    # Set this credential's parent
    def set_parent(self, cred):
        self.parent = cred
        self.updateRefID()

    ##
    # set the GID of the caller
    #
    # @param gid GID object of the caller

    def set_gid_caller(self, gid):
        self.gidCaller = gid
        # gid origin caller is the caller's gid by default
        self.gidOriginCaller = gid

    ##
    # get the GID of the object

    def get_gid_caller(self):
        if not self.gidCaller:
            self.decode()
        return self.gidCaller

    ##
    # set the GID of the object
    #
    # @param gid GID object of the object

    def set_gid_object(self, gid):
        self.gidObject = gid

    ##
    # get the GID of the object

    def get_gid_object(self):
        if not self.gidObject:
            self.decode()
        return self.gidObject
            
    ##
    # Expiration: an absolute UTC time of expiration (as either an int or string or datetime)
    # 
    def set_expiration(self, expiration):
        if isinstance(expiration, (int, float)):
            self.expiration = datetime.datetime.fromtimestamp(expiration)
        elif isinstance (expiration, datetime.datetime):
            self.expiration = expiration
        elif isinstance (expiration, StringTypes):
            self.expiration = utcparse (expiration)
        else:
            print "unexpected input type in Credential.set_expiration"


    ##
    # get the lifetime of the credential (always in datetime format)

    def get_expiration(self):
        if not self.expiration:
            self.decode()
        # at this point self.expiration is normalized as a datetime - DON'T call utcparse again
        return self.expiration

    ##
    # For legacy sake
    def get_lifetime(self):
        return self.get_expiration()
 
    ##
    # set the privileges
    #
    # @param privs either a comma-separated list of privileges of a Rights object

    def set_privileges(self, privs):
        if isinstance(privs, str):
            self.privileges = Rights(string = privs)
        else:
            self.privileges = privs        

    ##
    # return the privileges as a Rights object

    def get_privileges(self):
        if not self.privileges:
            self.decode()
        return self.privileges

    ##
    # determine whether the credential allows a particular operation to be
    # performed
    #
    # @param op_name string specifying name of operation ("lookup", "update", etc)

    def can_perform(self, op_name):
        rights = self.get_privileges()
        
        if not rights:
            return False

        return rights.can_perform(op_name)


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
        signed_cred.setAttribute("xsi:noNamespaceSchemaLocation", "http://www.planet-lab.org/resources/foam.sfa.credential.xsd")
        signed_cred.setAttribute("xsi:schemaLocation", "http://www.planet-lab.org/resources/foam.sfa.ext/policy/1 http://www.planet-lab.org/resources/foam.sfa.ext/policy/1/policy.xsd")

# PG says for those last 2:
#        signed_cred.setAttribute("xsi:noNamespaceSchemaLocation", "http://www.protogeni.net/resources/credential/credential.xsd")
#        signed_cred.setAttribute("xsi:schemaLocation", "http://www.protogeni.net/resources/credential/ext/policy/1 http://www.protogeni.net/resources/credential/ext/policy/1/policy.xsd")

        doc.appendChild(signed_cred)  
        
        # Fill in the <credential> bit        
        cred = doc.createElement("credential")
        cred.setAttribute("xml:id", self.get_refid())
        signed_cred.appendChild(cred)
        append_sub(doc, cred, "type", "privilege")
        append_sub(doc, cred, "serial", "8")
        append_sub(doc, cred, "owner_gid", self.gidCaller.save_to_string())
        append_sub(doc, cred, "owner_urn", self.gidCaller.get_urn())
        append_sub(doc, cred, "target_gid", self.gidObject.save_to_string())
        append_sub(doc, cred, "target_urn", self.gidObject.get_urn())
        append_sub(doc, cred, "uuid", "")
        if not self.expiration:
            self.set_expiration(datetime.datetime.utcnow() + datetime.timedelta(seconds=DEFAULT_CREDENTIAL_LIFETIME))
        self.expiration = self.expiration.replace(microsecond=0)
        append_sub(doc, cred, "expires", self.expiration.isoformat())
        privileges = doc.createElement("privileges")
        cred.appendChild(privileges)

        if self.privileges:
            rights = self.get_privileges()
            for right in rights.rights:
                priv = doc.createElement("privilege")
                append_sub(doc, priv, "name", right.kind)
                append_sub(doc, priv, "can_delegate", str(right.delegate).lower())
                privileges.appendChild(priv)

        # Add the parent credential if it exists
        if self.parent:
            sdoc = parseString(self.parent.get_xml())
            # If the root node is a signed-credential (it should be), then
            # get all its attributes and attach those to our signed_cred
            # node.
            # Specifically, PG and PLadd attributes for namespaces (which is reasonable),
            # and we need to include those again here or else their signature
            # no longer matches on the credential.
            # We expect three of these, but here we copy them all:
#        signed_cred.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
# and from PG (PL is equivalent, as shown above):
#        signed_cred.setAttribute("xsi:noNamespaceSchemaLocation", "http://www.protogeni.net/resources/credential/credential.xsd")
#        signed_cred.setAttribute("xsi:schemaLocation", "http://www.protogeni.net/resources/credential/ext/policy/1 http://www.protogeni.net/resources/credential/ext/policy/1/policy.xsd")

            # HOWEVER!
            # PL now also declares these, with different URLs, so
            # the code notices those attributes already existed with
            # different values, and complains.
            # This happens regularly on delegation now that PG and
            # PL both declare the namespace with different URLs.
            # If the content ever differs this is a problem,
            # but for now it works - different URLs (values in the attributes)
            # but the same actual schema, so using the PG schema
            # on delegated-to-PL credentials works fine.

            # Note: you could also not copy attributes
            # which already exist. It appears that both PG and PL
            # will actually validate a slicecred with a parent
            # signed using PG namespaces and a child signed with PL
            # namespaces over the whole thing. But I don't know
            # if that is a bug in xmlsec1, an accident since
            # the contents of the schemas are the same,
            # or something else, but it seems odd. And this works.
            parentRoot = sdoc.documentElement
            if parentRoot.tagName == "signed-credential" and parentRoot.hasAttributes():
                for attrIx in range(0, parentRoot.attributes.length):
                    attr = parentRoot.attributes.item(attrIx)
                    # returns the old attribute of same name that was
                    # on the credential
                    # Below throws InUse exception if we forgot to clone the attribute first
                    oldAttr = signed_cred.setAttributeNode(attr.cloneNode(True))
                    if oldAttr and oldAttr.value != attr.value:
                        msg = "Delegating cred from owner %s to %s over %s replaced attribute %s value '%s' with '%s'" % (self.parent.gidCaller.get_urn(), self.gidCaller.get_urn(), self.gidObject.get_urn(), oldAttr.name, oldAttr.value, attr.value)
                        #raise CredentialNotVerifiable("Can't encode new valid delegated credential: %s" % msg)

            p_cred = doc.importNode(sdoc.getElementsByTagName("credential")[0], True)
            p = doc.createElement("parent")
            p.appendChild(p_cred)
            cred.appendChild(p)
        # done handling parent credential

        # Create the <signatures> tag
        signatures = doc.createElement("signatures")
        signed_cred.appendChild(signatures)

        # Add any parent signatures
        if self.parent:
            for cur_cred in self.get_credential_list()[1:]:
                sdoc = parseString(cur_cred.get_signature().get_xml())
                ele = doc.importNode(sdoc.getElementsByTagName("Signature")[0], True)
                signatures.appendChild(ele)
                
        # Get the finished product
        self.xml = doc.toxml()


    def save_to_random_tmp_file(self):       
        fp, filename = mkstemp(suffix='cred', text=True)
        fp = os.fdopen(fp, "w")
        self.save_to_file(filename, save_parents=True, filep=fp)
        return filename
    
    def save_to_file(self, filename, save_parents=True, filep=None):
        if not self.xml:
            self.encode()
        if filep:
            f = filep 
        else:
            f = open(filename, "w")
        f.write(self.xml)
        f.close()

    def save_to_string(self, save_parents=True):
        if not self.xml:
            self.encode()
        return self.xml

    def get_refid(self):
        if not self.refid:
            self.refid = 'ref0'
        return self.refid

    def set_refid(self, rid):
        self.refid = rid

    ##
    # Figure out what refids exist, and update this credential's id
    # so that it doesn't clobber the others.  Returns the refids of
    # the parents.
    
    def updateRefID(self):
        if not self.parent:
            self.set_refid('ref0')
            return []
        
        refs = []

        next_cred = self.parent
        while next_cred:
            refs.append(next_cred.get_refid())
            if next_cred.parent:
                next_cred = next_cred.parent
            else:
                next_cred = None

        
        # Find a unique refid for this credential
        rid = self.get_refid()
        while rid in refs:
            val = int(rid[3:])
            rid = "ref%d" % (val + 1)

        # Set the new refid
        self.set_refid(rid)

        # Return the set of parent credential ref ids
        return refs

    def get_xml(self):
        if not self.xml:
            self.encode()
        return self.xml

    ##
    # Sign the XML file created by encode()
    #
    # WARNING:
    # In general, a signed credential obtained externally should
    # not be changed else the signature is no longer valid.  So, once
    # you have loaded an existing signed credential, do not call encode() or sign() on it.

    def sign(self):
        if not self.issuer_privkey:
            print "Cannot sign credential (no private key)"
            return
        if not self.issuer_gid:
            print "Cannot sign credential (no issuer gid)"
            return
        doc = parseString(self.get_xml())
        sigs = doc.getElementsByTagName("signatures")[0]

        # Create the signature template to be signed
        signature = Signature()
        signature.set_refid(self.get_refid())
        sdoc = parseString(signature.get_xml())        
        sig_ele = doc.importNode(sdoc.getElementsByTagName("Signature")[0], True)
        sigs.appendChild(sig_ele)

        self.xml = doc.toxml()


        # Split the issuer GID into multiple certificates if it's a chain
        chain = GID(filename=self.issuer_gid)
        gid_files = []
        while chain:
            gid_files.append(chain.save_to_random_tmp_file(False))
            if chain.get_parent():
                chain = chain.get_parent()
            else:
                chain = None


        # Call out to xmlsec1 to sign it
        ref = 'Sig_%s' % self.get_refid()
        filename = self.save_to_random_tmp_file()
        command='%s --sign --node-id "%s" --privkey-pem %s,%s %s' \
            % (self.xmlsec_path, ref, self.issuer_privkey, ",".join(gid_files), filename)
#        print 'command',command
        signed = os.popen(command).read()
        os.remove(filename)

        for gid_file in gid_files:
            os.remove(gid_file)

        self.xml = signed

        # This is no longer a legacy credential
        if self.legacy:
            self.legacy = None

        # Update signatures
        self.decode()       

        
    ##
    # Retrieve the attributes of the credential from the XML.
    # This is automatically called by the various get_* methods of
    # this class and should not need to be called explicitly.

    def decode(self):
        if not self.xml:
            return
        doc = parseString(self.xml)
        sigs = []
        signed_cred = doc.getElementsByTagName("signed-credential")

        # Is this a signed-cred or just a cred?
        if len(signed_cred) > 0:
            creds = signed_cred[0].getElementsByTagName("credential")
            signatures = signed_cred[0].getElementsByTagName("signatures")
            if len(signatures) > 0:
                sigs = signatures[0].getElementsByTagName("Signature")
        else:
            creds = doc.getElementsByTagName("credential")
        
        if creds is None or len(creds) == 0:
            # malformed cred file
            raise CredentialNotVerifiable("Malformed XML: No credential tag found")

        # Just take the first cred if there are more than one
        cred = creds[0]

        self.set_refid(cred.getAttribute("xml:id"))
        self.set_expiration(utcparse(getTextNode(cred, "expires")))
        self.gidCaller = GID(string=getTextNode(cred, "owner_gid"))
        self.gidObject = GID(string=getTextNode(cred, "target_gid"))   


        # Process privileges
        privs = cred.getElementsByTagName("privileges")[0]
        rlist = Rights()
        for priv in privs.getElementsByTagName("privilege"):
            kind = getTextNode(priv, "name")
            deleg = str2bool(getTextNode(priv, "can_delegate"))
            if kind == '*':
                # Convert * into the default privileges for the credential's type
                # Each inherits the delegatability from the * above
                _ , type = urn_to_hrn(self.gidObject.get_urn())
                rl = determine_rights(type, self.gidObject.get_urn())
                for r in rl.rights:
                    r.delegate = deleg
                    rlist.add(r)
            else:
                rlist.add(Right(kind.strip(), deleg))
        self.set_privileges(rlist)


        # Is there a parent?
        parent = cred.getElementsByTagName("parent")
        if len(parent) > 0:
            parent_doc = parent[0].getElementsByTagName("credential")[0]
            parent_xml = parent_doc.toxml()
            self.parent = Credential(string=parent_xml)
            self.updateRefID()

        # Assign the signatures to the credentials
        for sig in sigs:
            Sig = Signature(string=sig.toxml())

            for cur_cred in self.get_credential_list():
                if cur_cred.get_refid() == Sig.get_refid():
                    cur_cred.set_signature(Sig)
                                    
            
    ##
    # Verify
    #   trusted_certs: A list of trusted GID filenames (not GID objects!) 
    #                  Chaining is not supported within the GIDs by xmlsec1.
    #
    #   trusted_certs_required: Should usually be true. Set False means an
    #                 empty list of trusted_certs would still let this method pass.
    #                 It just skips xmlsec1 verification et al. Only used by some utils
    #    
    # Verify that:
    # . All of the signatures are valid and that the issuers trace back
    #   to trusted roots (performed by xmlsec1)
    # . The XML matches the credential schema
    # . That the issuer of the credential is the authority in the target's urn
    #    . In the case of a delegated credential, this must be true of the root
    # . That all of the gids presented in the credential are valid
    #    . Including verifying GID chains, and includ the issuer
    # . The credential is not expired
    #
    # -- For Delegates (credentials with parents)
    # . The privileges must be a subset of the parent credentials
    # . The privileges must have "can_delegate" set for each delegated privilege
    # . The target gid must be the same between child and parents
    # . The expiry time on the child must be no later than the parent
    # . The signer of the child must be the owner of the parent
    #
    # -- Verify does *NOT*
    # . ensure that an xmlrpc client's gid matches a credential gid, that
    #   must be done elsewhere
    #
    # @param trusted_certs: The certificates of trusted CA certificates
    def verify(self, trusted_certs=None, schema=None, trusted_certs_required=True):
        if not self.xml:
            self.decode()

        # validate against RelaxNG schema
        if HAVELXML and not self.legacy:
            if schema and os.path.exists(schema):
                tree = etree.parse(StringIO(self.xml))
                schema_doc = etree.parse(schema)
                
                xmlschema = etree.XMLSchema(schema_doc)
                #except Exception as e:
                #    print e
                if not xmlschema:#.validate(tree):
                    error = xmlschema.error_log.last_error
                    message = "%s: %s (line %s)" % (self.get_summary_tostring(), error.message, error.line)
                    raise CredentialNotVerifiable(message)

        if trusted_certs_required and trusted_certs is None:
            trusted_certs = []

#       trusted_cert_objects = [GID(filename=f) for f in trusted_certs]
        trusted_cert_objects = []
        ok_trusted_certs = []
        # If caller explicitly passed in None that means skip cert chain validation.
        # Strange and not typical
        if trusted_certs is not None:
            for f in trusted_certs:
                try:
                    # Failures here include unreadable files
                    # or non PEM files
                    trusted_cert_objects.append(GID(filename=f))
                    ok_trusted_certs.append(f)
                except Exception, exc:
                    print "Failed to load trusted cert from %s: %r" %(f, exc) 
            trusted_certs = ok_trusted_certs
        # Use legacy verification if this is a legacy credential
        if self.legacy:
            self.legacy.verify_chain(trusted_cert_objects)
            if self.legacy.client_gid:
                self.legacy.client_gid.verify_chain(trusted_cert_objects)
            if self.legacy.object_gid:
                self.legacy.object_gid.verify_chain(trusted_cert_objects)
            return True
        # make sure it is not expired
        if self.get_expiration() < datetime.datetime.utcnow():
            raise CredentialNotVerifiable("Credential %s expired at %s" % (self.get_summary_tostring(), self.expiration.isoformat()))
        # Verify the signatures
        filename = self.save_to_random_tmp_file()
        if trusted_certs is not None:
            cert_args = " ".join(['--trusted-pem %s' % x for x in trusted_certs])
        
        # If caller explicitly passed in None that means skip cert chain validation.
        # - Strange and not typical
        if trusted_certs is not None:
            # Verify the gids of this cred and of its parents
            for cur_cred in self.get_credential_list():
                cur_cred.get_gid_object().verify_chain(trusted_cert_objects)
                cur_cred.get_gid_caller().verify_chain(trusted_cert_objects)

        refs = []
        refs.append("Sig_%s" % self.get_refid())
        parentRefs = self.updateRefID()
        for ref in parentRefs:
            refs.append("Sig_%s" % ref)

        for ref in refs:
            # If caller explicitly passed in None that means skip xmlsec1 validation.
            # Strange and not typical
            if trusted_certs is None:
                break

#            print "Doing %s --verify --node-id '%s' %s %s 2>&1" % \
#                (self.xmlsec_path, ref, cert_args, filename)
            verified = os.popen('%s --verify --node-id "%s" %s %s 2>&1' \
                            % (self.xmlsec_path, ref, cert_args, filename)).read()
            if not verified.strip().startswith("OK"):
                # xmlsec errors have a msg= which is the interesting bit.
                mstart = verified.find("msg=")
                msg = ""
                if mstart > -1 and len(verified) > 4:
                    mstart = mstart + 4
                    mend = verified.find('\\', mstart)
                    msg = verified[mstart:mend]
                raise CredentialNotVerifiable("xmlsec1 error verifying cred %s using Signature ID %s: %s %s" % (self.get_summary_tostring(), ref, msg, verified.strip()))
        os.remove(filename)

        # Verify the parents (delegation)
        if self.parent:
            self.verify_parent(self.parent)

        # Make sure the issuer is the target's authority, and is
        # itself a valid GID
        self.verify_issuer(trusted_cert_objects)
        return True

    ##
    # Creates a list of the credential and its parents, with the root 
    # (original delegated credential) as the last item in the list
    def get_credential_list(self):    
        cur_cred = self
        list = []
        while cur_cred:
            list.append(cur_cred)
            if cur_cred.parent:
                cur_cred = cur_cred.parent
            else:
                cur_cred = None
        return list
    
    ##
    # Make sure the credential's target gid (a) was signed by or (b)
    # is the same as the entity that signed the original credential,
    # or (c) is an authority over the target's namespace.
    # Also ensure that the credential issuer / signer itself has a valid
    # GID signature chain (signed by an authority with namespace rights).
    def verify_issuer(self, trusted_gids):
        root_cred = self.get_credential_list()[-1]
        root_target_gid = root_cred.get_gid_object()
        root_cred_signer = root_cred.get_signature().get_issuer_gid()

        # Case 1:
        # Allow non authority to sign target and cred about target.
        #
        # Why do we need to allow non authorities to sign?
        # If in the target gid validation step we correctly
        # checked that the target is only signed by an authority,
        # then this is just a special case of case 3.
        # This short-circuit is the common case currently -
        # and cause GID validation doesn't check 'authority',
        # this allows users to generate valid slice credentials.
        if root_target_gid.is_signed_by_cert(root_cred_signer):
            # cred signer matches target signer, return success
            return

        # Case 2:
        # Allow someone to sign credential about themeselves. Used?
        # If not, remove this.
        #root_target_gid_str = root_target_gid.save_to_string()
        #root_cred_signer_str = root_cred_signer.save_to_string()
        #if root_target_gid_str == root_cred_signer_str:
        #    # cred signer is target, return success
        #    return

        # Case 3:

        # root_cred_signer is not the target_gid
        # So this is a different gid that we have not verified.
        # xmlsec1 verified the cert chain on this already, but
        # it hasn't verified that the gid meets the HRN namespace
        # requirements.
        # Below we'll ensure that it is an authority.
        # But we haven't verified that it is _signed by_ an authority
        # We also don't know if xmlsec1 requires that cert signers
        # are marked as CAs.

        # Note that if verify() gave us no trusted_gids then this
        # call will fail. So skip it if we have no trusted_gids
        if trusted_gids and len(trusted_gids) > 0:
            root_cred_signer.verify_chain(trusted_gids)
        else:
            print "No trusted gids. Cannot verify that cred signer is signed by a trusted authority. Skipping that check."

        # See if the signer is an authority over the domain of the target.
        # There are multiple types of authority - accept them all here
        # Maybe should be (hrn, type) = urn_to_hrn(root_cred_signer.get_urn())
        root_cred_signer_type = root_cred_signer.get_type()
        if (root_cred_signer_type.find('authority') == 0):
            #logger.debug('Cred signer is an authority')
            # signer is an authority, see if target is in authority's domain
            signerhrn = root_cred_signer.get_hrn()
            if hrn_authfor_hrn(signerhrn, root_target_gid.get_hrn()):
                return

        # We've required that the credential be signed by an authority
        # for that domain. Reasonable and probably correct.
        # A looser model would also allow the signer to be an authority
        # in my control framework - eg My CA or CH. Even if it is not
        # the CH that issued these, eg, user credentials.

        # Give up, credential does not pass issuer verification

        raise CredentialNotVerifiable("Could not verify credential owned by %s for object %s. Cred signer %s not the trusted authority for Cred target %s" % (self.gidCaller.get_urn(), self.gidObject.get_urn(), root_cred_signer.get_hrn(), root_target_gid.get_hrn()))


    ##
    # -- For Delegates (credentials with parents) verify that:
    # . The privileges must be a subset of the parent credentials
    # . The privileges must have "can_delegate" set for each delegated privilege
    # . The target gid must be the same between child and parents
    # . The expiry time on the child must be no later than the parent
    # . The signer of the child must be the owner of the parent        
    def verify_parent(self, parent_cred):
        # make sure the rights given to the child are a subset of the
        # parents rights (and check delegate bits)
        if not parent_cred.get_privileges().is_superset(self.get_privileges()):
            raise ChildRightsNotSubsetOfParent(("Parent cred ref %s rights " % parent_cred.get_refid()) +
                self.parent.get_privileges().save_to_string() + (" not superset of delegated cred %s ref %s rights " % (self.get_summary_tostring(), self.get_refid())) +
                self.get_privileges().save_to_string())

        # make sure my target gid is the same as the parent's
        if not parent_cred.get_gid_object().save_to_string() == \
           self.get_gid_object().save_to_string():
            raise CredentialNotVerifiable("Delegated cred %s: Target gid not equal between parent and child. Parent %s" % (self.get_summary_tostring(), parent_cred.get_summary_tostring()))

        # make sure my expiry time is <= my parent's
        if not parent_cred.get_expiration() >= self.get_expiration():
            raise CredentialNotVerifiable("Delegated credential %s expires after parent %s" % (self.get_summary_tostring(), parent_cred.get_summary_tostring()))

        # make sure my signer is the parent's caller
        if not parent_cred.get_gid_caller().save_to_string(False) == \
           self.get_signature().get_issuer_gid().save_to_string(False):
            raise CredentialNotVerifiable("Delegated credential %s not signed by parent %s's caller" % (self.get_summary_tostring(), parent_cred.get_summary_tostring()))
                
        # Recurse
        if parent_cred.parent:
            parent_cred.verify_parent(parent_cred.parent)


    def delegate(self, delegee_gidfile, caller_keyfile, caller_gidfile):
        """
        Return a delegated copy of this credential, delegated to the 
        specified gid's user.    
        """
        # get the gid of the object we are delegating
        object_gid = self.get_gid_object()
        object_hrn = object_gid.get_hrn()        
 
        # the hrn of the user who will be delegated to
        delegee_gid = GID(filename=delegee_gidfile)
        delegee_hrn = delegee_gid.get_hrn()
  
        #user_key = Keypair(filename=keyfile)
        #user_hrn = self.get_gid_caller().get_hrn()
        subject_string = "%s delegated to %s" % (object_hrn, delegee_hrn)
        dcred = Credential(subject=subject_string)
        dcred.set_gid_caller(delegee_gid)
        dcred.set_gid_object(object_gid)
        dcred.set_parent(self)
        dcred.set_expiration(self.get_expiration())
        dcred.set_privileges(self.get_privileges())
        dcred.get_privileges().delegate_all_privileges(True)
        #dcred.set_issuer_keys(keyfile, delegee_gidfile)
        dcred.set_issuer_keys(caller_keyfile, caller_gidfile)
        dcred.encode()
        dcred.sign()

        return dcred

    # only informative
    def get_filename(self):
        return getattr(self,'filename',None)

    ##
    # Dump the contents of a credential to stdout in human-readable format
    #
    # @param dump_parents If true, also dump the parent certificates
    def dump (self, *args, **kwargs):
        print self.dump_string(*args, **kwargs)


    def dump_string(self, dump_parents=False, show_xml=False):
        result=""
        result += "CREDENTIAL %s\n" % self.get_subject()
        filename=self.get_filename()
        if filename: result += "Filename %s\n"%filename
        result += "      privs: %s\n" % self.get_privileges().save_to_string()
        gidCaller = self.get_gid_caller()
        if gidCaller:
            result += "  gidCaller:\n"
            result += gidCaller.dump_string(8, dump_parents)

        if self.get_signature():
            print "  gidIssuer:"
            self.get_signature().get_issuer_gid().dump(8, dump_parents)

        if self.expiration:
            print "  expiration:", self.expiration.isoformat()

        gidObject = self.get_gid_object()
        if gidObject:
            result += "  gidObject:\n"
            result += gidObject.dump_string(8, dump_parents)

        if self.parent and dump_parents:
            result += "\nPARENT"
            result += self.parent.dump_string(True)

        if show_xml:
            try:
                tree = etree.parse(StringIO(self.xml))
                aside = etree.tostring(tree, pretty_print=True)
                result += "\nXML\n"
                result += aside
                result += "\nEnd XML\n"
            except:
                import traceback
                print "exc. Credential.dump_string / XML"
                traceback.print_exc()

        return result
