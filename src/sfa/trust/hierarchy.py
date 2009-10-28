##
# This module implements a hierarchy of authorities and performs a similar
# function as the "tree" module of the original geniwrapper prototype. An HRN
# is assumed to be a string of authorities separated by dots. For example,
# "planetlab.us.arizona.bakers". Each component of the HRN is a different
# authority, with the last component being a leaf in the tree.
#
# Each authority is stored in a subdirectory on the registry. Inside this
# subdirectory are several files:
#      *.GID - GID file
#      *.PKEY - private key file
#      *.DBINFO - database info
##

### $Id: hierarchy.py 14835 2009-08-20 17:33:58Z tmack $
### $URL: http://svn.planet-lab.org/svn/sfa/trunk/sfa/trust/hierarchy.py $

import os

from sfa.util.report import *
from sfa.trust.certificate import Keypair
from sfa.trust.credential import *
from sfa.trust.gid import GID, create_uuid

from sfa.util.misc import *
from sfa.util.config import Config
from sfa.util.sfaticket import SfaTicket

##
# The AuthInfo class contains the information for an authority. This information
# includes the GID, private key, and database connection information.

class AuthInfo:
    hrn = None
    gid_object = None
    gid_filename = None
    privkey_filename = None
    dbinfo_filename = None

    ##
    # Initialize and authority object.
    #
    # @param hrn the human readable name of the authority
    # @param gid_filename the filename containing the GID
    # @param privkey_filename the filename containing the private key
    # @param dbinfo_filename the filename containing the database info

    def __init__(self, hrn, gid_filename, privkey_filename, dbinfo_filename):
        self.hrn = hrn
        self.set_gid_filename(gid_filename)
        self.privkey_filename = privkey_filename
        self.dbinfo_filename = dbinfo_filename

    ##
    # Set the filename of the GID
    #
    # @param fn filename of file containing GID

    def set_gid_filename(self, fn):
        self.gid_filename = fn
        self.gid_object = None

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
    # Get the dbinfo in the form of a dictionary

    def get_dbinfo(self):
        f = file(self.dbinfo_filename)
        dict = eval(f.read())
        f.close()
        return dict

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
# contains the GID, pkey, and dbinfo files for that authority (as well as
# subdirectories for each sub-authority)

class Hierarchy:
    ##
    # Create the hierarchy object.
    #
    # @param basedir the base directory to store the hierarchy in

    def __init__(self, basedir = None):
        if not basedir:
            self.config = Config()
            basedir = os.path.join(self.config.SFA_BASE_DIR, "authorities")
        self.basedir = basedir
    ##
    # Given a hrn, return the filenames of the GID, private key, and dbinfo
    # files.
    #
    # @param hrn the human readable name of the authority

    def get_auth_filenames(self, hrn):
        leaf = get_leaf(hrn)
        parent_hrn = get_authority(hrn)
        directory = os.path.join(self.basedir, hrn.replace(".", "/"))

        gid_filename = os.path.join(directory, leaf+".gid")
        privkey_filename = os.path.join(directory, leaf+".pkey")
        dbinfo_filename = os.path.join(directory, leaf+".dbinfo")

        return (directory, gid_filename, privkey_filename, dbinfo_filename)

    ##
    # Check to see if an authority exists. An authority exists if it's disk
    # files exist.
    #
    # @param the human readable name of the authority to check

    def auth_exists(self, hrn):
        (directory, gid_filename, privkey_filename, dbinfo_filename) = \
            self.get_auth_filenames(hrn)
        
        return os.path.exists(gid_filename) and \
               os.path.exists(privkey_filename) and \
               os.path.exists(dbinfo_filename)

    ##
    # Create an authority. A private key for the authority and the associated
    # GID are created and signed by the parent authority.
    #
    # @param hrn the human readable name of the authority to create
    # @param create_parents if true, also create the parents if they do not exist

    def create_auth(self, hrn, create_parents=False):
        trace("Hierarchy: creating authority: " + hrn)

        # create the parent authority if necessary
        parent_hrn = get_authority(hrn)
        if (parent_hrn) and (not self.auth_exists(parent_hrn)) and (create_parents):
            self.create_auth(parent_hrn, create_parents)

        (directory, gid_filename, privkey_filename, dbinfo_filename) = \
            self.get_auth_filenames(hrn)

        # create the directory to hold the files
        try:
            os.makedirs(directory)
        # if the path already exists then pass
        except OSError, (errno, strerr):
            if errno == 17:
                pass

        if os.path.exists(privkey_filename):
            print "using existing key", privkey_filename, "for authority", hrn
            pkey = Keypair(filename = privkey_filename)
        else:
            pkey = Keypair(create = True)
            pkey.save_to_file(privkey_filename)

        gid = self.create_gid(hrn, create_uuid(), pkey)
        gid.save_to_file(gid_filename, save_parents=True)

        # XXX TODO: think up a better way for the dbinfo to work

        dbinfo = Config().get_plc_dbinfo()
        dbinfo_file = file(dbinfo_filename, "w")
        dbinfo_file.write(str(dbinfo))
        dbinfo_file.close()

    ##
    # Return the AuthInfo object for the specified authority. If the authority
    # does not exist, then an exception is thrown. As a side effect, disk files
    # and a subdirectory may be created to store the authority.
    #
    # @param hrn the human readable name of the authority to create.

    def get_auth_info(self, hrn):
        #trace("Hierarchy: getting authority: " + hrn)
   
        if not self.auth_exists(hrn):
            raise MissingAuthority(hrn)

        (directory, gid_filename, privkey_filename, dbinfo_filename) = \
            self.get_auth_filenames(hrn)

        auth_info = AuthInfo(hrn, gid_filename, privkey_filename, dbinfo_filename)

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

    def create_gid(self, hrn, uuid, pkey):
        gid = GID(subject=hrn, uuid=uuid, hrn=hrn)

        parent_hrn = get_authority(hrn)
        if not parent_hrn or hrn == self.config.SFA_INTERFACE_HRN:
            # if there is no parent hrn, then it must be self-signed. this
            # is where we terminate the recursion
            gid.set_issuer(pkey, hrn)
        else:
            # we need the parent's private key in order to sign this GID
            parent_auth_info = self.get_auth_info(parent_hrn)
            gid.set_issuer(parent_auth_info.get_pkey_object(), parent_auth_info.hrn)
            gid.set_parent(parent_auth_info.get_gid_object())

        gid.set_pubkey(pkey)
        gid.encode()
        gid.sign()

        return gid

    ##
    # Refresh a GID. The primary use of this function is to refresh the
    # the expiration time of the GID. It may also be used to change the HRN,
    # UUID, or Public key of the GID.
    #
    # @param gid the GID to refresh
    # @param hrn if !=None, change the hrn
    # @param uuid if !=None, change the uuid
    # @param pubkey if !=None, change the public key

    def refresh_gid(self, gid, hrn=None, uuid=None, pubkey=None):
        # TODO: compute expiration time of GID, refresh it if necessary
        gid_is_expired = False

        # update the gid if we need to
        if gid_is_expired or hrn or uuid or pubkey:
            if not hrn:
                hrn = gid.get_hrn()
            if not uuid:
                uuid = gid.get_uuid()
            if not pubkey:
                pubkey = gid.get_pubkey()

            gid = self.create_gid(hrn, uuid, pubkey)

        return gid

    ##
    # Retrieve an authority credential for an authority. The authority
    # credential will contain the authority privilege and will be signed by
    # the authority's parent.
    #
    # @param hrn the human readable name of the authority
    # @param authority type of credential to return (authority | sa | ma)

    def get_auth_cred(self, hrn, kind="authority"):
        auth_info = self.get_auth_info(hrn)
        gid = auth_info.get_gid_object()

        cred = Credential(subject=hrn)
        cred.set_gid_caller(gid)
        cred.set_gid_object(gid)
        cred.set_privileges(kind)
        cred.set_delegate(True)
        cred.set_pubkey(auth_info.get_gid_object().get_pubkey())

        parent_hrn = get_authority(hrn)
        if not parent_hrn or hrn == self.config.SFA_INTERFACE_HRN:
            # if there is no parent hrn, then it must be self-signed. this
            # is where we terminate the recursion
            cred.set_issuer(auth_info.get_pkey_object(), hrn)
        else:
            # we need the parent's private key in order to sign this GID
            parent_auth_info = self.get_auth_info(parent_hrn)
            cred.set_issuer(parent_auth_info.get_pkey_object(), parent_auth_info.hrn)
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
    # @param hrn the human readable name of the authority

    def get_auth_ticket(self, hrn):
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

