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

### $Id$
### $URL$

import os
import datetime
from xml.dom.minidom import Document, parseString
from tempfile import mkstemp
from expedient.common.federation.sfa.trust.certificate import Keypair
from expedient.common.federation.sfa.trust.credential_legacy import CredentialLegacy
from expedient.common.federation.sfa.trust.rights import *
from expedient.common.federation.sfa.trust.gid import *
from expedient.common.federation.sfa.util.faults import *

from expedient.common.federation.sfa.util.sfalogging import logger
from dateutil.parser import parse



# Two years, in seconds 
DEFAULT_CREDENTIAL_LIFETIME = 60 * 60 * 24 * 365 * 2


# TODO:
# . make privs match between PG and PL
# . Need to add support for other types of credentials, e.g. tickets


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

##
# Convert a string into a bool

def str2bool(str):
    if str.lower() in ['yes','true','1']:
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
        doc = parseString(self.xml)
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

def filter_creds_by_caller(creds, caller_hrn):
        """
        Returns a list of creds who's gid caller matches the
        specified caller hrn
        """
        if not isinstance(creds, list):
            creds = [creds]
        caller_creds = []
        for cred in creds:
            try:
                tmp_cred = Credential(string=cred)
                if tmp_cred.get_gid_caller().get_hrn() == caller_hrn:
                    caller_creds.append(cred)
            except:
                pass
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

    def get_subject(self):
        if not self.gidObject:
            self.decode()
        return self.gidObject.get_subject()   

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
            # Default to two years
            self.set_lifetime(DEFAULT_CREDENTIAL_LIFETIME)
        else:
            self.set_lifetime(int(lifetime))
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
    # set the lifetime of this credential
    #
    # @param lifetime lifetime of credential
    # . if lifeTime is a datetime object, it is used for the expiration time
    # . if lifeTime is an integer value, it is considered the number of seconds
    #   remaining before expiration

    def set_lifetime(self, lifeTime):
        if isinstance(lifeTime, int):
            self.expiration = datetime.timedelta(seconds=lifeTime) + datetime.datetime.utcnow()
        else:
            self.expiration = lifeTime

    ##
    # get the lifetime of the credential (in datetime format)

    def get_lifetime(self):
        if not self.expiration:
            self.decode()
        return self.expiration

 
    ##
    # set the privileges
    #
    # @param privs either a comma-separated list of privileges of a RightList object

    def set_privileges(self, privs):
        if isinstance(privs, str):
            self.privileges = RightList(string = privs)
        else:
            self.privileges = privs
        

    ##
    # return the privileges as a RightList object

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
            self.set_lifetime(DEFAULT_CREDENTIAL_LIFETIME)
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
            p_cred = doc.importNode(sdoc.getElementsByTagName("credential")[0], True)
            p = doc.createElement("parent")
            p.appendChild(p_cred)
            cred.appendChild(p)


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
        if not self.issuer_privkey or not self.issuer_gid:
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
        signed = os.popen('%s --sign --node-id "%s" --privkey-pem %s,%s %s' \
                 % (self.xmlsec_path, ref, self.issuer_privkey, ",".join(gid_files), filename)).read()
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
            cred = signed_cred[0].getElementsByTagName("credential")[0]
            signatures = signed_cred[0].getElementsByTagName("signatures")
            if len(signatures) > 0:
                sigs = signatures[0].getElementsByTagName("Signature")
        else:
            cred = doc.getElementsByTagName("credential")[0]
        

        self.set_refid(cred.getAttribute("xml:id"))
        self.set_lifetime(parse(getTextNode(cred, "expires")))
        self.gidCaller = GID(string=getTextNode(cred, "owner_gid"))
        self.gidObject = GID(string=getTextNode(cred, "target_gid"))   


        # Process privileges
        privs = cred.getElementsByTagName("privileges")[0]
        rlist = RightList()
        for priv in privs.getElementsByTagName("privilege"):
            kind = getTextNode(priv, "name")
            deleg = str2bool(getTextNode(priv, "can_delegate"))
            if kind == '*':
                # Convert * into the default privileges for the credential's type                
                _ , type = urn_to_hrn(self.gidObject.get_urn())
                rl = rlist.determine_rights(type, self.gidObject.get_urn())
                for r in rl.rights:
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
    # Verify that:
    # . All of the signatures are valid and that the issuers trace back
    #   to trusted roots (performed by xmlsec1)
    # . The XML matches the credential schema
    # . That the issuer of the credential is the authority in the target's urn
    #    . In the case of a delegated credential, this must be true of the root
    # . That all of the gids presented in the credential are valid
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
    def verify(self, trusted_certs):
        if not self.xml:
            self.decode()        

#        trusted_cert_objects = [GID(filename=f) for f in trusted_certs]
        trusted_cert_objects = []
        ok_trusted_certs = []
        for f in trusted_certs:
            try:
                # Failures here include unreadable files
                # or non PEM files
                trusted_cert_objects.append(GID(filename=f))
                ok_trusted_certs.append(f)
            except Exception, exc:
                import traceback
                logger.error("Failed to load trusted cert from %s: %r", f, exc)
                logger.debug(traceback.format_exc(exc))
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
        if self.get_lifetime() < datetime.datetime.utcnow():
            raise CredentialNotVerifiable("Credential expired at %s" % self.expiration.isoformat())

        # Verify the signatures
        filename = self.save_to_random_tmp_file()
        cert_args = " ".join(['--trusted-pem %s' % x for x in trusted_certs])

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
            verified = os.popen('%s --verify --node-id "%s" %s %s 2>&1' \
                            % (self.xmlsec_path, ref, cert_args, filename)).read()
            if not verified.strip().startswith("OK"):
                raise CredentialNotVerifiable("xmlsec1 error verifying cert: " + verified)
        os.remove(filename)

        # Verify the parents (delegation)
        if self.parent:
            self.verify_parent(self.parent)

        # Make sure the issuer is the target's authority
        self.verify_issuer()
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
    # Make sure the credential's target gid was signed by (or is the same) the entity that signed
    # the original credential or an authority over that namespace.
    def verify_issuer(self):                
        root_cred = self.get_credential_list()[-1]
        root_target_gid = root_cred.get_gid_object()
        root_cred_signer = root_cred.get_signature().get_issuer_gid()

        if root_target_gid.is_signed_by_cert(root_cred_signer):
            # cred signer matches target signer, return success
            return

        root_target_gid_str = root_target_gid.save_to_string()
        root_cred_signer_str = root_cred_signer.save_to_string()
        if root_target_gid_str == root_cred_signer_str:
            # cred signer is target, return success
            return

        # See if it the signer is an authority over the domain of the target
        # Maybe should be (hrn, type) = urn_to_hrn(root_cred_signer.get_urn())
        root_cred_signer_type = root_cred_signer.get_type()
        if (root_cred_signer_type == 'authority'):
            #logger.debug('Cred signer is an authority')
            # signer is an authority, see if target is in authority's domain
            hrn = root_cred_signer.get_hrn()
            if root_target_gid.get_hrn().startswith(hrn):
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
            raise ChildRightsNotSubsetOfParent(
                self.parent.get_privileges().save_to_string() + " " +
                self.get_privileges().save_to_string())

        # make sure my target gid is the same as the parent's
        if not parent_cred.get_gid_object().save_to_string() == \
           self.get_gid_object().save_to_string():
            raise CredentialNotVerifiable("Target gid not equal between parent and child")

        # make sure my expiry time is <= my parent's
        if not parent_cred.get_lifetime() >= self.get_lifetime():
            raise CredentialNotVerifiable("Delegated credential expires after parent")

        # make sure my signer is the parent's caller
        if not parent_cred.get_gid_caller().save_to_string(False) == \
           self.get_signature().get_issuer_gid().save_to_string(False):
            raise CredentialNotVerifiable("Delegated credential not signed by parent caller")
                
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
        dcred.set_lifetime(self.get_lifetime())
        dcred.set_privileges(self.get_privileges())
        dcred.get_privileges().delegate_all_privileges(True)
        #dcred.set_issuer_keys(keyfile, delegee_gidfile)
        dcred.set_issuer_keys(caller_keyfile, caller_gidfile)
        dcred.encode()
        dcred.sign()

        return dcred 
    ##
    # Dump the contents of a credential to stdout in human-readable format
    #
    # @param dump_parents If true, also dump the parent certificates

    def dump(self, dump_parents=False):
        print "CREDENTIAL", self.get_subject()

        print "      privs:", self.get_privileges().save_to_string()

        print "  gidCaller:"
        gidCaller = self.get_gid_caller()
        if gidCaller:
            gidCaller.dump(8, dump_parents)

        print "  gidObject:"
        gidObject = self.get_gid_object()
        if gidObject:
            gidObject.dump(8, dump_parents)


        if self.parent and dump_parents:
            print "PARENT",
            self.parent.dump_parents()

