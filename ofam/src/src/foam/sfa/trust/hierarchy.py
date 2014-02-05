##
# This module implements a hierarchy of authorities and performs a similar
# function as the "tree" module of the original SFA prototype. An HRN
# is assumed to be a string of authorities separated by dots. For example,
# "planetlab.us.arizona.bakers". Each component of the HRN is a different
# authority, with the last component being a leaf in the tree.
#
# Each authority is stored in a subdirectory on the registry. Inside this
# subdirectory are several files:
#      *.GID - GID file
#      *.PKEY - private key file
##

import os

from foam.sfa.util.faults import MissingAuthority
#from foam.sfa.util.foam.sfa.ogging import logger
from foam.sfa.util.xrn import get_leaf, get_authority, hrn_to_urn, urn_to_hrn
from foam.sfa.trust.certificate import Keypair
from foam.sfa.trust.credential import Credential
from foam.sfa.trust.gid import GID, create_uuid
from foam.sfa.sfa_config import config
from foam.sfa.trust.sfaticket import SfaTicket
#XXX:Use the ClearingHouse
#from foam.sfa.setUp import setup_config as auth_config
##
# The AuthInfo class contains the information for an authority. This information
# includes the GID, private key, and database connection information.

class AuthInfo:
    hrn = None
    gid_object = None
    gid_filename = None
    privkey_filename = None
    ##
    # Initialize and authority object.
    #
    # @param xrn the human readable name of the authority (urn will be converted to hrn)
    # @param gid_filename the filename containing the GID
    # @param privkey_filename the filename containing the private key

    def __init__(self, xrn, gid_filename, privkey_filename):
        hrn, type = urn_to_hrn(xrn)
        self.hrn = hrn
        self.set_gid_filename(gid_filename)
        self.privkey_filename = privkey_filename

    ##
    # Set the filename of the GID
    #
    # @param fn filename of file containing GID

    def set_gid_filename(self, fn):
        self.gid_filename = fn
        self.gid_object = None

    def get_privkey_filename(self):
        return self.privkey_filename

    def get_gid_filename(self):
        return self.gid_filename

    ##
    # Get the GID in the form of a GID object

    def get_gid_object(self):
        if not self.gid_object:
            self.gid_object = GID(filename = self.gid_filename)
        return self.gid_object

    ##
    # Get the private key in the form of a Keypair object

    def get_pkey_object(self):
        return Keypair(filename = self.privkey_filename)

    ##
    # Replace the GID with a new one. The file specified by gid_filename is
    # overwritten with the new GID object
    #
    # @param gid object containing new GID

    def update_gid_object(self, gid):
        gid.save_to_file(self.gid_filename)
        self.gid_object = gid

##
# The Hierarchy class is responsible for managing the tree of authorities.
# Each authority is a node in the tree and exists as an AuthInfo object.
#
# The tree is stored on disk in a hierarchical manner than reflects the
# structure of the tree. Each authority is a subdirectory, and each subdirectory
# contains the GID and pkey files for that authority (as well as
# subdirectories for each sub-authority)

class Hierarchy:
    ##
    # Create the hierarchy object.
    #
    # @param basedir the base directory to store the hierarchy in

    def __init__(self, basedir = None):
        self.config = config
        if not basedir:
            basedir = os.path.join(self.config.SFA_DATA_DIR, "authorities")
        self.basedir = basedir
    ##
    # Given a hrn, return the filenames of the GID, private key
    # files.
    #
    # @param xrn the human readable name of the authority (urn will be convertd to hrn)

    def get_auth_filenames(self, xrn):
        hrn, type = urn_to_hrn(xrn)
        leaf = get_leaf(hrn)
        parent_hrn = get_authority(hrn)
        directory = os.path.join(self.basedir, hrn.replace(".", "/"))

        gid_filename = os.path.join(directory, leaf+".gid")
        privkey_filename = os.path.join(directory, leaf+".pkey")

        return (directory, gid_filename, privkey_filename)

    ##
    # Check to see if an authority exists. An authority exists if it's disk
    # files exist.
    #
    # @param the human readable name of the authority to check

    def auth_exists(self, xrn):
        hrn, type = urn_to_hrn(xrn) 
        (directory, gid_filename, privkey_filename) = \
            self.get_auth_filenames(hrn)
        print directory, gid_filename, privkey_filename
        
        return os.path.exists(gid_filename) and os.path.exists(privkey_filename) 

    ##
    # Create an authority. A private key for the authority and the associated
    # GID are created and signed by the parent authority.
    #
    # @param xrn the human readable name of the authority to create (urn will be converted to hrn) 
    # @param create_parents if true, also create the parents if they do not exist

    def create_auth(self, xrn, create_parents=False):
        hrn, type = urn_to_hrn(str(xrn))

        # create the parent authority if necessary
        parent_hrn = get_authority(hrn)
        parent_urn = hrn_to_urn(parent_hrn, 'authority')
        if (parent_hrn) and (not self.auth_exists(parent_urn)) and (create_parents):
            self.create_auth(parent_urn, create_parents)
        (directory, gid_filename, privkey_filename,) = \
            self.get_auth_filenames(hrn)

        # create the directory to hold the files
        try:
            os.makedirs(directory)
        # if the path already exists then pass
        except OSError, (errno, strerr):
            if errno == 17:
                pass

        if os.path.exists(privkey_filename):
            pkey = Keypair(filename = privkey_filename)
        else:
            pkey = Keypair(create = True)
            pkey.save_to_file(privkey_filename)

        gid = self.create_gid(xrn, create_uuid(), pkey)
        gid.save_to_file(gid_filename, save_parents=True)

    def create_top_level_auth(self, hrn=None):
        """
        Create top level records (includes root and sub authorities (local/remote)
        """
        # create the authority if it doesnt alrady exist
        if not self.auth_exists(hrn):
            self.create_auth(hrn, create_parents=True)
            
        
    def get_interface_auth_info(self, create=True):
        hrn = self.config.SFA_INTERFACE_HRN
        if not self.auth_exists(hrn):
            if create==True:
                self.create_top_level_auth(hrn) 
            else:
                raise MissingAuthority(hrn)
        return self.get_auth_info(hrn)
    ##
    # Return the AuthInfo object for the specified authority. If the authority
    # does not exist, then an exception is thrown. As a side effect, disk files
    # and a subdirectory may be created to store the authority.
    #
    # @param xrn the human readable name of the authority to create (urn will be converted to hrn).

    def get_auth_info(self, xrn):
        hrn, type = urn_to_hrn(xrn)
        if not self.auth_exists(hrn):
            raise MissingAuthority(hrn)

        (directory, gid_filename, privkey_filename, ) = \
            self.get_auth_filenames(hrn)

        auth_info = AuthInfo(hrn, gid_filename, privkey_filename)

        # check the GID and see if it needs to be refreshed
        gid = auth_info.get_gid_object()
        gid_refreshed = self.refresh_gid(gid)
        if gid != gid_refreshed:
            auth_info.update_gid_object(gid_refreshed)

        return auth_info

    ##
    # Create a new GID. The GID will be signed by the authority that is it's
    # immediate parent in the hierarchy (and recursively, the parents' GID
    # will be signed by its parent)
    #
    # @param hrn the human readable name to store in the GID
    # @param uuid the unique identifier to store in the GID
    # @param pkey the public key to store in the GID

    def create_gid(self, xrn, uuid, pkey, CA=False, email=None):
        hrn, type = urn_to_hrn(xrn)
        if not type:
            type = 'authority'
        parent_hrn = get_authority(hrn)
        # Using hrn_to_urn() here to make sure the urn is in the right format
        # If xrn was a hrn instead of a urn, then the gid's urn will be
        # of type None 
        urn = hrn_to_urn(hrn, type)
        subject = self.get_subject(hrn)
        if not subject:
            subject = hrn
        gid = GID(subject=subject, uuid=uuid, hrn=hrn, urn=urn, email=email)
        # is this a CA cert
        if hrn == self.config.SFA_INTERFACE_HRN or not parent_hrn:
            # root or sub authority  
            gid.set_intermediate_ca(True)
        elif type and 'authority' in type:
            # authority type
            gid.set_intermediate_ca(False)
        elif CA:
            gid.set_intermediate_ca(True)
        else:
            gid.set_intermediate_ca(False)

        # set issuer
        if not parent_hrn or hrn == self.config.SFA_INTERFACE_HRN:
            # if there is no parent hrn, then it must be self-signed. this
            # is where we terminate the recursion
            gid.set_issuer(pkey, subject)
        else:
            # we need the parent's private key in order to sign this GID
            parent_auth_info = self.get_auth_info(parent_hrn)
            parent_gid = parent_auth_info.get_gid_object()
            gid.set_issuer(parent_auth_info.get_pkey_object(), parent_gid.get_extended_subject())
            gid.set_parent(parent_auth_info.get_gid_object())

        gid.set_pubkey(pkey)
        gid.encode()
        gid.sign()

        return gid

    def get_subject(self,hrn):
        if len(hrn.split('.'))>1:
            subject = auth_config.SUBJECT
        else:
            subject = auth_config.PARENT_SUBJECT 
        return subject


   ##
    # Refresh a GID. The primary use of this function is to refresh the
    # the expiration time of the GID. It may also be used to change the HRN,
    # UUID, or Public key of the GID.
    #
    # @param gid the GID to refresh
    # @param hrn if !=None, change the hrn
    # @param uuid if !=None, change the uuid
    # @param pubkey if !=None, change the public key
    def refresh_gid(self, gid, xrn=None, uuid=None, pubkey=None):
        # TODO: compute expiration time of GID, refresh it if necessary
        gid_is_expired = False

        # update the gid if we need to
        if gid_is_expired or xrn or uuid or pubkey:
            
            if not xrn:
                xrn = gid.get_urn()
            if not uuid:
                uuid = gid.get_uuid()
            if not pubkey:
                pubkey = gid.get_pubkey()

            gid = self.create_gid(xrn, uuid, pubkey)

        return gid

    ##
    # Retrieve an authority credential for an authority. The authority
    # credential will contain the authority privilege and will be signed by
    # the authority's parent.
    #
    # @param hrn the human readable name of the authority (urn is converted to hrn)
    # @param authority type of credential to return (authority | sa | ma)

    def get_auth_cred(self, xrn, kind="authority"):
        hrn, type = urn_to_hrn(xrn) 
        auth_info = self.get_auth_info(hrn)
        gid = auth_info.get_gid_object()

        cred = Credential(subject=hrn)
        cred.set_gid_caller(gid)
        cred.set_gid_object(gid)
        cred.set_privileges(kind)
        cred.get_privileges().delegate_all_privileges(True)
        #cred.set_pubkey(auth_info.get_gid_object().get_pubkey())

        parent_hrn = get_authority(hrn)
        if not parent_hrn or hrn == self.config.SFA_INTERFACE_HRN:
            # if there is no parent hrn, then it must be self-signed. this
            # is where we terminate the recursion
            cred.set_issuer_keys(auth_info.get_privkey_filename(), auth_info.get_gid_filename())
        else:
            # we need the parent's private key in order to sign this GID
            parent_auth_info = self.get_auth_info(parent_hrn)
            cred.set_issuer_keys(parent_auth_info.get_privkey_filename(), parent_auth_info.get_gid_filename())

            
            cred.set_parent(self.get_auth_cred(parent_hrn, kind))

        cred.encode()
        cred.sign()

        return cred
    ##
    # Retrieve an authority ticket. An authority ticket is not actually a
    # redeemable ticket, but only serves the purpose of being included as the
    # parent of another ticket, in order to provide a chain of authentication
    # for a ticket.
    #
    # This looks almost the same as get_auth_cred, but works for tickets
    # XXX does similarity imply there should be more code re-use?
    #
    # @param xrn the human readable name of the authority (urn is converted to hrn)

    def get_auth_ticket(self, xrn):
        hrn, type = urn_to_hrn(xrn)
        auth_info = self.get_auth_info(hrn)
        gid = auth_info.get_gid_object()

        ticket = SfaTicket(subject=hrn)
        ticket.set_gid_caller(gid)
        ticket.set_gid_object(gid)
        ticket.set_delegate(True)
        ticket.set_pubkey(auth_info.get_gid_object().get_pubkey())

        parent_hrn = get_authority(hrn)
        if not parent_hrn:
            # if there is no parent hrn, then it must be self-signed. this
            # is where we terminate the recursion
            ticket.set_issuer(auth_info.get_pkey_object(), hrn)
        else:
            # we need the parent's private key in order to sign this GID
            parent_auth_info = self.get_auth_info(parent_hrn)
            ticket.set_issuer(parent_auth_info.get_pkey_object(), parent_auth_info.hrn)
            ticket.set_parent(self.get_auth_cred(parent_hrn))

        ticket.encode()
        ticket.sign()

        return ticket

