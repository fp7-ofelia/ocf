# Thierry Parmentelat -- INRIA
#
# a minimal library for writing "lightweight" SFA clients
#

# xxx todo
# this library should probably check for the expiration date of the various
# certificates and automatically retrieve fresh ones when expired

import sys
import os,os.path
from datetime import datetime
from sfa.utils.xrn import Xrn

#import sfa.util.sfalogging
# importing sfa.utils.faults does pull a lot of stuff 
# OTOH it's imported from Certificate anyways, so..
from sfa.utils.faults import RecordNotFound

#from sfa.client.sfaserverproxy import SfaServerProxy

# see optimizing dependencies below
from sfa.trust.certificate import Keypair, Certificate
from sfa.trust.credential import Credential
from sfa.trust.gid import GID

########## 
# a helper class to implement the bootstrapping of crypto. material
# assuming we are starting from scratch on the client side 
# what's needed to complete a full slice creation cycle
# (**) prerequisites: 
#  (*) a local private key 
#  (*) the corresp. public key in the registry 
# (**) step1: a self-signed certificate
#      default filename is <hrn>.sscert
# (**) step2: a user credential
#      obtained at the registry with GetSelfCredential
#      using the self-signed certificate as the SSL cert
#      default filename is <hrn>.user.cred
# (**) step3: a registry-provided certificate (i.e. a GID)
#      obtained at the registry using Resolve
#      using the step2 credential as credential
#      default filename is <hrn>.user.gid
#
# From that point on, the GID is used as the SSL certificate
# and the following can be done
#
# (**) retrieve a slice (or authority) credential 
#      obtained at the registry with GetCredential
#      using the (step2) user-credential as credential
#      default filename is <hrn>.<type>.cred
# (**) retrieve a slice (or authority) GID 
#      obtained at the registry with Resolve
#      using the (step2) user-credential as credential
#      default filename is <hrn>.<type>.cred


########## Implementation notes
#
# (*) decorators
#
# this implementation is designed as a guideline for 
# porting to other languages
#
# the decision to go for decorators aims at focusing 
# on the core of what needs to be done when everything
# works fine, and to take caching and error management 
# out of the way
# 
# for non-pythonic developers, it should be enough to 
# implement the bulk of this code, namely the _produce methods
# and to add caching and error management by whichever means 
# is available, including inline 
#
# (*) self-signed certificates
# 
# still with other languages in mind, we've tried to keep the
# dependencies to the rest of the code as low as possible
# 
# however this still relies on the sfa.trust.certificate module
# for the initial generation of a self-signed-certificate that
# is associated to the user's ssh-key
# (for user-friendliness, and for smooth operations with planetlab, 
# the usage model is to reuse an existing keypair)
# 
# there might be a more portable, i.e. less language-dependant way, to
# implement this step by exec'ing the openssl command.
# a known successful attempt at this approach that worked 
# for Java is documented below
# http://nam.ece.upatras.gr/fstoolkit/trac/wiki/JavaSFAClient
#
####################

class SfaClientException (Exception): pass

class SfaClientBootstrap:

    # dir is mandatory but defaults to '.'
    def __init__ (self, user_hrn, registry_url, dir=None, 
                  verbose=False, timeout=None, logger=None):
        self.hrn=user_hrn
        self.registry_url=registry_url
        if dir is None: dir="."
        self.dir=dir
        self.verbose=verbose
        self.timeout=timeout
        # default for the logger is to use the global sfa logger
        #if logger is None: 
         #   logger = sfa.util.sfalogging.logger
        #self.logger=logger

    ######################################## *_produce methods
    ### step1
    # unconditionnally create a self-signed certificate
    def self_signed_cert_produce (self,output):
        self.assert_private_key()
        private_key_filename = self.private_key_filename()
        keypair=Keypair(filename=private_key_filename)
        self_signed = Certificate (subject = self.hrn)
        self_signed.set_pubkey (keypair)
        self_signed.set_issuer (keypair, self.hrn)
        self_signed.sign ()
        self_signed.save_to_file (output)
        #self.logger.debug("SfaClientBootstrap: Created self-signed certificate for %s in %s"%\
                              #(self.hrn,output))
        return output

    ### step2 
    # unconditionnally retrieve my credential (GetSelfCredential)
    # we always use the self-signed-cert as the SSL cert
    def my_credential_produce (self, output):
        self.assert_self_signed_cert()
        certificate_filename = self.self_signed_cert_filename()
        certificate_string = self.plain_read (certificate_filename)
        self.assert_private_key()
        #registry_proxy = SfaServerProxy (self.registry_url, self.private_key_filename(),
         #                                certificate_filename)
        try:
            credential_string=registry_proxy.GetSelfCredential (certificate_string, self.hrn, "user")
        except:
            # some urns hrns may replace non hierarchy delimiters '.' with an '_' instead of escaping the '.'
            hrn = Xrn(self.hrn).get_hrn().replace('\.', '_') 
            credential_string=registry_proxy.GetSelfCredential (certificate_string, hrn, "user")
        self.plain_write (output, credential_string)
        #self.logger.debug("SfaClientBootstrap: Wrote result of GetSelfCredential in %s"%output)
        return output

    ### step3
    # unconditionnally retrieve my GID - use the general form 
    def my_gid_produce (self,output):
        return self.gid_produce (output, self.hrn, "user")

    ### retrieve any credential (GetCredential) unconditionnal form
    # we always use the GID as the SSL cert
    def credential_produce (self, output, hrn, type):
        self.assert_my_gid()
        certificate_filename = self.my_gid_filename()
        self.assert_private_key()
        registry_proxy = SfaServerProxy (self.registry_url, self.private_key_filename(),
                                         certificate_filename)
        self.assert_my_credential()
        my_credential_string = self.my_credential_string()
        credential_string=registry_proxy.GetCredential (my_credential_string, hrn, type)
        self.plain_write (output, credential_string)
        #self.logger.debug("SfaClientBootstrap: Wrote result of GetCredential in %s"%output)
        return output

    def slice_credential_produce (self, output, hrn):
        return self.credential_produce (output, hrn, "slice")

    def authority_credential_produce (self, output, hrn):
        return self.credential_produce (output, hrn, "authority")

    ### retrieve any gid (Resolve) - unconditionnal form
    # use my GID when available as the SSL cert, otherwise the self-signed
    def gid_produce (self, output, hrn, type ):
        try:
            self.assert_my_gid()
            certificate_filename = self.my_gid_filename()
        except:
            self.assert_self_signed_cert()
            certificate_filename = self.self_signed_cert_filename()
            
        self.assert_private_key()
        registry_proxy = SfaServerProxy (self.registry_url, self.private_key_filename(),
                                         certificate_filename)
        credential_string=self.plain_read (self.my_credential())
        records = registry_proxy.Resolve (hrn, credential_string)
        records=[record for record in records if record['type']==type]
        if not records:
            raise RecordNotFound, "hrn %s (%s) unknown to registry %s"%(hrn,type,self.registry_url)
        record=records[0]
        self.plain_write (output, record['gid'])
        #self.logger.debug("SfaClientBootstrap: Wrote GID for %s (%s) in %s"% (hrn,type,output))
        return output


    # Returns True if credential file is valid. Otherwise return false.
    def validate_credential(self, filename):
        valid = True
        cred = Credential(filename=filename)
        # check if credential is expires
        if cred.get_expiration() < datetime.now():
            valid = False
        return valid
    

    #################### public interface
    
    # return my_gid, run all missing steps in the bootstrap sequence
    def bootstrap_my_gid (self):
        self.self_signed_cert()
        self.my_credential()
        return self.my_gid()

    # once we've bootstrapped we can use this object to issue any other SFA call
    # always use my gid
    def server_proxy (self, url):
        self.assert_my_gid()
        return SfaServerProxy (url, self.private_key_filename(), self.my_gid_filename(),
                               verbose=self.verbose, timeout=self.timeout)

    # now in some cases the self-signed is enough
    def server_proxy_simple (self, url):
        self.assert_self_signed_cert()
        return SfaServerProxy (url, self.private_key_filename(), self.self_signed_cert_filename(),
                               verbose=self.verbose, timeout=self.timeout)

    # this method can optionnally be invoked to ensure proper
    # installation of the private key that belongs to this user
    # installs private_key in working dir with expected name -- preserve mode
    # typically user_private_key would be ~/.ssh/id_rsa
    # xxx should probably check the 2 files are identical
    def init_private_key_if_missing (self, user_private_key):
        private_key_filename=self.private_key_filename()
        if not os.path.isfile (private_key_filename):
            key=self.plain_read(user_private_key)
            self.plain_write(private_key_filename, key)
            os.chmod(private_key_filename,os.stat(user_private_key).st_mode)
            #self.logger.debug("SfaClientBootstrap: Copied private key from %s into %s"%\
                                  #(user_private_key,private_key_filename))
        
    #################### private details
    # stupid stuff
    def fullpath (self, file): return os.path.join (self.dir,file)

    # the expected filenames for the various pieces
    def private_key_filename (self): 
        return self.fullpath ("%s.pkey" % Xrn.unescape(self.hrn))
    def self_signed_cert_filename (self): 
        return self.fullpath ("%s.sscert"%self.hrn)
    def my_credential_filename (self):
        return self.credential_filename (self.hrn, "user")
    def credential_filename (self, hrn, type): 
        return self.fullpath ("%s.%s.cred"%(hrn,type))
    def slice_credential_filename (self, hrn): 
        return self.credential_filename(hrn,'slice')
    def authority_credential_filename (self, hrn): 
        return self.credential_filename(hrn,'authority')
    def my_gid_filename (self):
        return self.gid_filename (self.hrn, "user")
    def gid_filename (self, hrn, type): 
        return self.fullpath ("%s.%s.gid"%(hrn,type))
    

# optimizing dependencies
# originally we used classes GID or Credential or Certificate 
# like e.g. 
#        return Credential(filename=self.my_credential()).save_to_string()
# but in order to make it simpler to other implementations/languages..
    def plain_read (self, filename):
        infile=file(filename,"r")
        result=infile.read()
        infile.close()
        return result

    def plain_write (self, filename, contents):
        outfile=file(filename,"w")
        result=outfile.write(contents)
        outfile.close()

    def assert_filename (self, filename, kind):
        if not os.path.isfile (filename):
            raise IOError,"Missing %s file %s"%(kind,filename)
        return True
        
    def assert_private_key (self): return self.assert_filename (self.private_key_filename(),"private key")
    def assert_self_signed_cert (self): return self.assert_filename (self.self_signed_cert_filename(),"self-signed certificate")
    def assert_my_credential (self): return self.assert_filename (self.my_credential_filename(),"user's credential")
    def assert_my_gid (self): return self.assert_filename (self.my_gid_filename(),"user's GID")


    # decorator to make up the other methods
    def get_or_produce (filename_method, produce_method, validate_method=None):
        # default validator returns true
        def wrap (f):
            def wrapped (self, *args, **kw):
                filename=filename_method (self, *args, **kw)
                if os.path.isfile ( filename ):
                    if not validate_method:
                        return filename
                    elif validate_method(self, filename): 
                        return filename
                    else:
                        # remove invalid file
                        #self.logger.warning ("Removing %s - has expired"%filename)
                        os.unlink(filename) 
                try:
                    produce_method (self, filename, *args, **kw)
                    return filename
                except IOError:
                    raise 
                except :
                    error = sys.exc_info()[:2]
                    message="Could not produce/retrieve %s (%s -- %s)"%\
                        (filename,error[0],error[1])
                    #self.logger.log_exc(message)
                    raise Exception, message
            return wrapped
        return wrap

    @get_or_produce (self_signed_cert_filename, self_signed_cert_produce)
    def self_signed_cert (self): pass

    @get_or_produce (my_credential_filename, my_credential_produce, validate_credential)
    def my_credential (self): pass

    @get_or_produce (my_gid_filename, my_gid_produce)
    def my_gid (self): pass

    @get_or_produce (credential_filename, credential_produce, validate_credential)
    def credential (self, hrn, type): pass

    @get_or_produce (slice_credential_filename, slice_credential_produce, validate_credential)
    def slice_credential (self, hrn): pass

    @get_or_produce (authority_credential_filename, authority_credential_produce, validate_credential)
    def authority_credential (self, hrn): pass

    @get_or_produce (gid_filename, gid_produce)
    def gid (self, hrn, type ): pass


    # get the credentials as strings, for inserting as API arguments
    def my_credential_string (self): 
        self.my_credential()
        return self.plain_read(self.my_credential_filename())
    def slice_credential_string (self, hrn): 
        self.slice_credential(hrn)
        return self.plain_read(self.slice_credential_filename(hrn))
    def authority_credential_string (self, hrn): 
        self.authority_credential(hrn)
        return self.plain_read(self.authority_credential_filename(hrn))

    # for consistency
    def private_key (self):
        self.assert_private_key()
        return self.private_key_filename()

    def delegate_credential_string (self, original_credential, to_hrn, to_type='authority'):
        """
        sign a delegation credential to someone else

        original_credential : typically one's user- or slice- credential to be delegated to s/b else
        to_hrn : the hrn of the person that will be allowed to do stuff on our behalf
        to_type : goes with to_hrn, usually 'user' or 'authority'

        returns a string with the delegated credential

        this internally uses self.my_gid()
        it also retrieves the gid for to_hrn/to_type
        and uses Credential.delegate()"""

        # the gid and hrn of the object we are delegating
        if isinstance (original_credential, str):
            original_credential = Credential (string=original_credential)
        original_gid = original_credential.get_gid_object()
        original_hrn = original_gid.get_hrn()

        if not original_credential.get_privileges().get_all_delegate():
            #self.logger.error("delegate_credential_string: original credential %s does not have delegate bit set"%original_hrn)
            return

        # the delegating user's gid
        my_gid = self.my_gid()

        # retrieve the GID for the entity that we're delegating to
        to_gidfile = self.gid (to_hrn,to_type)
#        to_gid = GID ( to_gidfile )
#        to_hrn = delegee_gid.get_hrn()
#        print 'to_hrn',to_hrn
        delegated_credential = original_credential.delegate(to_gidfile, self.private_key(), my_gid)
        return delegated_credential.save_to_string(save_parents=True)
