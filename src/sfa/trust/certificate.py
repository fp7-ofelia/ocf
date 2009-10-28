##
# Geniwrapper uses two crypto libraries: pyOpenSSL and M2Crypto to implement
# the necessary crypto functionality. Ideally just one of these libraries
# would be used, but unfortunately each of these libraries is independently
# lacking. The pyOpenSSL library is missing many necessary functions, and
# the M2Crypto library has crashed inside of some of the functions. The
# design decision is to use pyOpenSSL whenever possible as it seems more
# stable, and only use M2Crypto for those functions that are not possible
# in pyOpenSSL.
#
# This module exports two classes: Keypair and Certificate.
##
#
### $Id: certificate.py 15293 2009-10-14 00:23:42Z tmack $
### $URL: http://svn.planet-lab.org/svn/sfa/trunk/sfa/trust/certificate.py $
#

import os
import tempfile
import base64
import traceback
from OpenSSL import crypto
import M2Crypto
from M2Crypto import X509
from M2Crypto import EVP

from sfa.util.faults import *

def convert_public_key(key):
    keyconvert_path = "/usr/bin/keyconvert"
    if not os.path.isfile(keyconvert_path):
        raise IOError, "Could not find keyconvert in %s" % keyconvert_path

    # we can only convert rsa keys 
    if "ssh-dss" in key:
        print "XXX: DSA key encountered, ignoring"
        return None
    
    (ssh_f, ssh_fn) = tempfile.mkstemp()
    ssl_fn = tempfile.mktemp()
    os.write(ssh_f, key)
    os.close(ssh_f)

    cmd = keyconvert_path + " " + ssh_fn + " " + ssl_fn
    os.system(cmd)

    # this check leaves the temporary file containing the public key so
    # that it can be expected to see why it failed.
    # TODO: for production, cleanup the temporary files
    if not os.path.exists(ssl_fn):
        report.trace("  failed to convert key from " + ssh_fn + " to " + ssl_fn)
        return None

    k = Keypair()
    try:
        k.load_pubkey_from_file(ssl_fn)
    except:
        print "XXX: Error while converting key: ", key
        traceback.print_exc()
        k = None

    # remove the temporary files
    os.remove(ssh_fn)
    os.remove(ssl_fn)

    return k

##
# Public-private key pairs are implemented by the Keypair class.
# A Keypair object may represent both a public and private key pair, or it
# may represent only a public key (this usage is consistent with OpenSSL).

class Keypair:
   key = None       # public/private keypair
   m2key = None     # public key (m2crypto format)

   ##
   # Creates a Keypair object
   # @param create If create==True, creates a new public/private key and
   #     stores it in the object
   # @param string If string!=None, load the keypair from the string (PEM)
   # @param filename If filename!=None, load the keypair from the file

   def __init__(self, create=False, string=None, filename=None):
      if create:
         self.create()
      if string:
         self.load_from_string(string)
      if filename:
         self.load_from_file(filename)

   ##
   # Create a RSA public/private key pair and store it inside the keypair object

   def create(self):
      self.key = crypto.PKey()
      self.key.generate_key(crypto.TYPE_RSA, 1024)

   ##
   # Save the private key to a file
   # @param filename name of file to store the keypair in

   def save_to_file(self, filename):
      open(filename, 'w').write(self.as_pem())

   ##
   # Load the private key from a file. Implicity the private key includes the public key.

   def load_from_file(self, filename):
      buffer = open(filename, 'r').read()
      self.load_from_string(buffer)

   ##
   # Load the private key from a string. Implicitly the private key includes the public key.

   def load_from_string(self, string):
      self.key = crypto.load_privatekey(crypto.FILETYPE_PEM, string)
      self.m2key = M2Crypto.EVP.load_key_string(string)

   ##
   #  Load the public key from a string. No private key is loaded. 

   def load_pubkey_from_file(self, filename):
      # load the m2 public key
      m2rsakey = M2Crypto.RSA.load_pub_key(filename)
      self.m2key = M2Crypto.EVP.PKey()
      self.m2key.assign_rsa(m2rsakey)

      # create an m2 x509 cert
      m2name = M2Crypto.X509.X509_Name()
      m2name.add_entry_by_txt(field="CN", type=0x1001, entry="junk", len=-1, loc=-1, set=0)
      m2x509 = M2Crypto.X509.X509()
      m2x509.set_pubkey(self.m2key)
      m2x509.set_serial_number(0)
      m2x509.set_issuer_name(m2name)
      m2x509.set_subject_name(m2name)
      ASN1 = M2Crypto.ASN1.ASN1_UTCTIME()
      ASN1.set_time(500)
      m2x509.set_not_before(ASN1)
      m2x509.set_not_after(ASN1)
      junk_key = Keypair(create=True)
      m2x509.sign(pkey=junk_key.get_m2_pkey(), md="sha1")

      # convert the m2 x509 cert to a pyopenssl x509
      m2pem = m2x509.as_pem()
      pyx509 = crypto.load_certificate(crypto.FILETYPE_PEM, m2pem)

      # get the pyopenssl pkey from the pyopenssl x509
      self.key = pyx509.get_pubkey()

   ##
   # Load the public key from a string. No private key is loaded.

   def load_pubkey_from_string(self, string):
      (f, fn) = tempfile.mkstemp()
      os.write(f, string)
      os.close(f)
      self.load_pubkey_from_file(fn)
      os.remove(fn)

   ##
   # Return the private key in PEM format.

   def as_pem(self):
      return crypto.dump_privatekey(crypto.FILETYPE_PEM, self.key)

   ##
   # Return an M2Crypto key object

   def get_m2_pkey(self):
      if not self.m2key:
         self.m2key = M2Crypto.EVP.load_key_string(self.as_pem())
      return self.m2key

   ##
   # Returns a string containing the public key represented by this object.

   def get_pubkey_string(self):
      m2pkey = self.get_m2_pkey()
      return base64.b64encode(m2pkey.as_der())

   ##
   # Return an OpenSSL pkey object

   def get_openssl_pkey(self):
      return self.key

   ##
   # Given another Keypair object, return TRUE if the two keys are the same.

   def is_same(self, pkey):
      return self.as_pem() == pkey.as_pem()

   def sign_string(self, data):
      k = self.get_m2_pkey()
      k.sign_init()
      k.sign_update(data)
      return base64.b64encode(k.sign_final())

   def verify_string(self, data, sig):
      k = self.get_m2_pkey()
      k.verify_init()
      k.verify_update(data)
      return M2Crypto.m2.verify_final(k.ctx, base64.b64decode(sig), k.pkey)

   def compute_hash(self, value):
      return self.sign_string(str(value))      

##
# The certificate class implements a general purpose X509 certificate, making
# use of the appropriate pyOpenSSL or M2Crypto abstractions. It also adds
# several addition features, such as the ability to maintain a chain of
# parent certificates, and storage of application-specific data.
#
# Certificates include the ability to maintain a chain of parents. Each
# certificate includes a pointer to it's parent certificate. When loaded
# from a file or a string, the parent chain will be automatically loaded.
# When saving a certificate to a file or a string, the caller can choose
# whether to save the parent certificates as well.

class Certificate:
   digest = "md5"

   data = None
   cert = None
   issuerKey = None
   issuerSubject = None
   parent = None

   separator="-----parent-----"

   ##
   # Create a certificate object.
   #
   # @param create If create==True, then also create a blank X509 certificate.
   # @param subject If subject!=None, then create a blank certificate and set
   #     it's subject name.
   # @param string If string!=None, load the certficate from the string.
   # @param filename If filename!=None, load the certficiate from the file.

   def __init__(self, create=False, subject=None, string=None, filename=None):
       if create or subject:
           self.create()
       if subject:
           self.set_subject(subject)
       if string:
           self.load_from_string(string)
       if filename:
           self.load_from_file(filename)

   ##
   # Create a blank X509 certificate and store it in this object.

   def create(self):
       self.cert = crypto.X509()
       self.cert.set_serial_number(1)
       self.cert.gmtime_adj_notBefore(0)
       self.cert.gmtime_adj_notAfter(60*60*24*365*5) # five years

   ##
   # Given a pyOpenSSL X509 object, store that object inside of this
   # certificate object.

   def load_from_pyopenssl_x509(self, x509):
       self.cert = x509

   ##
   # Load the certificate from a string

   def load_from_string(self, string):
       # if it is a chain of multiple certs, then split off the first one and
       # load it
       parts = string.split(Certificate.separator, 1)
       self.cert = crypto.load_certificate(crypto.FILETYPE_PEM, parts[0])

       # if there are more certs, then create a parent and let the parent load
       # itself from the remainder of the string
       if len(parts) > 1:
           self.parent = self.__class__()
           self.parent.load_from_string(parts[1])

   ##
   # Load the certificate from a file

   def load_from_file(self, filename):
       file = open(filename)
       string = file.read()
       self.load_from_string(string)

   ##
   # Save the certificate to a string.
   #
   # @param save_parents If save_parents==True, then also save the parent certificates.

   def save_to_string(self, save_parents=False):
       string = crypto.dump_certificate(crypto.FILETYPE_PEM, self.cert)
       if save_parents and self.parent:
          string = string + Certificate.separator + self.parent.save_to_string(save_parents)
       return string

   ##
   # Save the certificate to a file.
   # @param save_parents If save_parents==True, then also save the parent certificates.

   def save_to_file(self, filename, save_parents=False):
       string = self.save_to_string(save_parents=save_parents)
       open(filename, 'w').write(string)

   ##
   # Sets the issuer private key and name
   # @param key Keypair object containing the private key of the issuer
   # @param subject String containing the name of the issuer
   # @param cert (optional) Certificate object containing the name of the issuer

   def set_issuer(self, key, subject=None, cert=None):
       self.issuerKey = key
       if subject:
          # it's a mistake to use subject and cert params at the same time
          assert(not cert)
          if isinstance(subject, dict) or isinstance(subject, str):
             req = crypto.X509Req()
             reqSubject = req.get_subject()
             if (isinstance(subject, dict)):
                for key in reqSubject.keys():
                    setattr(reqSubject, key, name[key])
             else:
                setattr(reqSubject, "CN", subject)
             subject = reqSubject
             # subject is not valid once req is out of scope, so save req
             self.issuerReq = req
       if cert:
          # if a cert was supplied, then get the subject from the cert
          subject = cert.cert.get_issuer()
       assert(subject)
       self.issuerSubject = subject

   ##
   # Get the issuer name

   def get_issuer(self, which="CN"):
       x = self.cert.get_issuer()
       return getattr(x, which)

   ##
   # Set the subject name of the certificate

   def set_subject(self, name):
       req = crypto.X509Req()
       subj = req.get_subject()
       if (isinstance(name, dict)):
           for key in name.keys():
               setattr(subj, key, name[key])
       else:
           setattr(subj, "CN", name)
       self.cert.set_subject(subj)
   ##
   # Get the subject name of the certificate

   def get_subject(self, which="CN"):
       x = self.cert.get_subject()
       return getattr(x, which)

   ##
   # Get the public key of the certificate.
   #
   # @param key Keypair object containing the public key

   def set_pubkey(self, key):
       assert(isinstance(key, Keypair))
       self.cert.set_pubkey(key.get_openssl_pkey())

   ##
   # Get the public key of the certificate.
   # It is returned in the form of a Keypair object.

   def get_pubkey(self):
       m2x509 = X509.load_cert_string(self.save_to_string())
       pkey = Keypair()
       pkey.key = self.cert.get_pubkey()
       pkey.m2key = m2x509.get_pubkey()
       return pkey

   ##
   # Add an X509 extension to the certificate. Add_extension can only be called
   # once for a particular extension name, due to limitations in the underlying
   # library.
   #
   # @param name string containing name of extension
   # @param value string containing value of the extension

   def add_extension(self, name, critical, value):
       ext = crypto.X509Extension (name, critical, value)
       self.cert.add_extensions([ext])

   ##
   # Get an X509 extension from the certificate

   def get_extension(self, name):
       # pyOpenSSL does not have a way to get extensions
       m2x509 = X509.load_cert_string(self.save_to_string())
       value = m2x509.get_ext(name).get_value()
       return value

   ##
   # Set_data is a wrapper around add_extension. It stores the parameter str in
   # the X509 subject_alt_name extension. Set_data can only be called once, due
   # to limitations in the underlying library.

   def set_data(self, str):
       # pyOpenSSL only allows us to add extensions, so if we try to set the
       # same extension more than once, it will not work
       if self.data != None:
          raise "cannot set subjectAltName more than once"
       self.data = str
       self.add_extension("subjectAltName", 0, "URI:http://" + str)

   ##
   # Return the data string that was previously set with set_data

   def get_data(self):
       if self.data:
           return self.data

       try:
           uri = self.get_extension("subjectAltName")
       except LookupError:
           self.data = None
           return self.data

       if not uri.startswith("URI:http://"):
           raise "bad encoding in subjectAltName"
       self.data = uri[11:]
       return self.data

   ##
   # Sign the certificate using the issuer private key and issuer subject previous set with set_issuer().

   def sign(self):
       assert self.cert != None
       assert self.issuerSubject != None
       assert self.issuerKey != None
       self.cert.set_issuer(self.issuerSubject)
       self.cert.sign(self.issuerKey.get_openssl_pkey(), self.digest)

    ##
    # Verify the authenticity of a certificate.
    # @param pkey is a Keypair object representing a public key. If Pkey
    #     did not sign the certificate, then an exception will be thrown.

   def verify(self, pkey):
       # pyOpenSSL does not have a way to verify signatures
       m2x509 = X509.load_cert_string(self.save_to_string())
       m2pkey = pkey.get_m2_pkey()
       # verify it
       return m2x509.verify(m2pkey)

       # XXX alternatively, if openssl has been patched, do the much simpler:
       # try:
       #   self.cert.verify(pkey.get_openssl_key())
       #   return 1
       # except:
       #   return 0

   ##
   # Return True if pkey is identical to the public key that is contained in the certificate.
   # @param pkey Keypair object

   def is_pubkey(self, pkey):
       return self.get_pubkey().is_same(pkey)

   ##
   # Given a certificate cert, verify that this certificate was signed by the
   # public key contained in cert. Throw an exception otherwise.
   #
   # @param cert certificate object

   def is_signed_by_cert(self, cert):
       k = cert.get_pubkey()
       result = self.verify(k)
       return result

   ##
   # Set the parent certficiate.
   #
   # @param p certificate object.

   def set_parent(self, p):
        self.parent = p

   ##
   # Return the certificate object of the parent of this certificate.

   def get_parent(self):
        return self.parent

   ##
   # Verification examines a chain of certificates to ensure that each parent
   # signs the child, and that some certificate in the chain is signed by a
   # trusted certificate.
   #
   # Verification is a basic recursion: <pre>
   #     if this_certificate was signed by trusted_certs:
   #         return
   #     else
   #         return verify_chain(parent, trusted_certs)
   # </pre>
   #
   # At each recursion, the parent is tested to ensure that it did sign the
   # child. If a parent did not sign a child, then an exception is thrown. If
   # the bottom of the recursion is reached and the certificate does not match
   # a trusted root, then an exception is thrown.
   #
   # @param Trusted_certs is a list of certificates that are trusted.
   #

   def verify_chain(self, trusted_certs = None):
        # Verify a chain of certificates. Each certificate must be signed by
        # the public key contained in it's parent. The chain is recursed
        # until a certificate is found that is signed by a trusted root.

        # TODO: verify expiration time
        #print "====Verify Chain====="
        # if this cert is signed by a trusted_cert, then we are set
        for trusted_cert in trusted_certs:
            #print "***************"
            # TODO: verify expiration of trusted_cert ?
            #print "CLIENT CERT", self.dump()
            #print "TRUSTED CERT", trusted_cert.dump()
            #print "Client is signed by Trusted?", self.is_signed_by_cert(trusted_cert)
            if self.is_signed_by_cert(trusted_cert):
                #print self.get_subject(), "is signed by a root"
                return

        # if there is no parent, then no way to verify the chain
        if not self.parent:
            #print self.get_subject(), "has no parent"
            raise CertMissingParent(self.get_subject())

        # if it wasn't signed by the parent...
        if not self.is_signed_by_cert(self.parent):
            #print self.get_subject(), "is not signed by parent"
            return CertNotSignedByParent(self.get_subject())

        # if the parent isn't verified...
        self.parent.verify_chain(trusted_certs)

        return
