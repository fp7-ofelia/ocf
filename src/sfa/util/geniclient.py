##
# This module implements the client-side of the Geni API. Stubs are provided
# that convert the supplied parameters to the necessary format and send them
# via XMLRPC to a Geni Server.
#
# TODO: Investigate ways to combine this with existing PLC API?
##

### $Id: geniclient.py 15170 2009-09-27 00:49:17Z tmack $
### $URL: http://svn.planet-lab.org/svn/sfa/tags/sfa-0.9-5/sfa/util/geniclient.py $

from sfa.trust.gid import *
from sfa.trust.credential import *
from sfa.util.record import *
from sfa.util.sfaticket import SfaTicket

##
# The GeniClient class provides stubs for executing Geni operations. A given
# client object connects to one server. To connect to multiple servers, create
# multiple GeniClient objects.
#
# The Geni protocol uses an HTTPS connection, and the client's side of the
# connection uses his private key. Generally, this private key must match the
# public key that is containing in the GID that the client is providing for
# those functions that take a GID.

class GeniClient:
    ##
    # Create a new GeniClient object.
    #
    # @param url is the url of the server
    # @param key_file = private key file of client
    # @param cert_file = x.509 cert containing the client's public key. This
    #      could be a GID certificate, or any x.509 cert.
    # @param protocol The ORPC protocol to use. Can be "soap" or "xmlrpc"

    def __init__(self, url, key_file, cert_file, protocol="xmlrpc"):
       self.url = url
       self.key_file = key_file
       self.cert_file = cert_file

       if (protocol=="xmlrpc"):
           import xmlrpcprotocol  
           self.server = xmlrpcprotocol.get_server(self.url, self.key_file, self.cert_file)
       elif (protocol=="soap"):
           import soapprotocol
           self.server = soapprotocol.get_server(self.url, self.key_file, self.cert_file)
       else:
           raise Exception("Attempted use of undefined protocol %s"%protocol)


    # -------------------------------------------------------------------------
    # Registry Interface
    # -------------------------------------------------------------------------

    ##
    # Create a new GID. For MAs and SAs that are physically located on the
    # registry, this allows a owner/operator/PI to create a new GID and have it
    # signed by his respective authority.
    #
    # @param cred credential of caller
    # @param name hrn for new GID
    # @param uuid unique identifier for new GID
    # @param pkey_string public-key string (TODO: why is this a string and not a keypair object?)
    #
    # @return a GID object

    def create_gid(self, cred, name, uuid, pkey_string):
        gid_str = self.server.create_gid(cred.save_to_string(save_parents=True), name, uuid, pkey_string)
        return GID(string=gid_str)

    ##
    # Retrieve the GID for an object. This function looks up a record in the
    # registry and returns the GID of the record if it exists.
    # TODO: Is this function needed? It's a shortcut for Resolve()
    #
    # @param name hrn to look up
    #
    # @return a GID object

    def get_gid(self, name):
       gid_str_list = self.server.get_gid(name)
       gid_list = []
       for str in gid_str_list:
           gid_list.append(GID(string=str))
       return gid_list

    ##
    # Get_self_credential a degenerate version of get_credential used by a
    # client to get his initial credential when he doesn't have one. This is
    # the same as get_credential(..., cred=None,...).
    #
    # The registry ensures that the client is the principal that is named by
    # (type, name) by comparing the public key in the record's GID to the
    # private key used to encrypt the client-side of the HTTPS connection. Thus
    # it is impossible for one principal to retrieve another principal's
    # credential without having the appropriate private key.
    #
    # @param type type of object (user | slice | sa | ma | node
    # @param name human readable name of object
    #
    # @return a credential object

    def get_self_credential(self, type, name):
        cred_str = self.server.get_self_credential(type, name)
        return Credential(string = cred_str)

    ##
    # Retrieve a credential for an object.
    #
    # If cred==None, then the behavior reverts to get_self_credential()
    #
    # @param cred credential object specifying rights of the caller
    # @param type type of object (user | slice | sa | ma | node)
    # @param name human readable name of object
    #
    # @return a credental object

    def get_credential(self, cred, type, name):
        if cred:
            cred = cred.save_to_string(save_parents=True) 
        cred_str = self.server.get_credential(cred, type, name)
        return Credential(string = cred_str)

    ##
    # List the records in an authority. The objectGID in the supplied credential
    # should name the authority that will be listed.
    #
    # @param cred credential object specifying rights of the caller
    #
    # @return list of record objects

    def list(self, cred, auth_hrn, caller_cred=None):
        result_dict_list = self.server.list(cred.save_to_string(save_parents=True), auth_hrn, caller_cred)
        result_rec_list = []
        for dict in result_dict_list:
             result_rec_list.append(GeniRecord(dict=dict))
        return result_rec_list

    ##
    # Register an object with the registry. In addition to being stored in the
    # Geni database, the appropriate records will also be created in the
    # PLC databases.
    #
    #
    #
    # @param cred credential object specifying rights of the caller
    # @param record to register
    #
    # @return GID object for the newly-registered record

    def register(self, cred, record, caller_cred=None):
        gid_str = self.server.register(cred.save_to_string(save_parents=True), record.as_dict(), caller_cred)
        return GID(string = gid_str)

    
    ##
    # Register a peer object with the registry. 
    #
    #
    # @param cred credential object specifying rights of the caller
    # @param record to register
    #
    # @return GID object for the newly-registered record

    def register_peer_object(self, cred, record, caller_cred=None):
        return self.server.register_peer_object(cred.save_to_string(save_parents=True), record, caller_cred)

    ##
    # Remove an object from the registry. If the object represents a PLC object,
    # then the PLC records will also be removed.
    #
    # @param cred credential object specifying rights of the caller
    # @param type
    # @param hrn

    def remove(self, cred, type, hrn, caller_cred=None):
        return self.server.remove(cred.save_to_string(save_parents=True), type, hrn, caller_cred)

    ##
    # Remove a peer object from the registry. If the object represents a PLC object,
    # then the PLC records will also be removed.
    #
    # @param cred credential object specifying rights of the caller
    # @param type
    # @param hrn

    def remove_peer_object(self, cred, record, caller_cred=None):
        result = self.server.remove_peer_object(cred.save_to_string(save_parents=True), record, caller_cred)
        return result

    ##
    # Resolve an object in the registry. A given HRN may have multiple records
    # associated with it, and therefore multiple records may be returned. The
    # caller should check the type fields of the records to find the one that
    # he is interested in.
    #
    # @param cred credential object specifying rights of the caller
    # @param name human readable name of object

    def resolve(self, cred, name, caller_cred=None):
        result_dict_list = self.server.resolve(cred.save_to_string(save_parents=True), name, caller_cred)
        result_rec_list = []
        for dict in result_dict_list:
            if dict['type'] in ['authority']:
                result_rec_list.append(AuthorityRecord(dict=dict))
            elif dict['type'] in ['node']:
                result_rec_list.append(NodeRecord(dict=dict))
            elif dict['type'] in ['slice']:
                result_rec_list.append(SliceRecord(dict=dict))
            elif dict['type'] in ['user']:
                result_rec_list.append(UserRecord(dict=dict))
            else:
                result_rec_list.append(GeniRecord(dict=dict))
        return result_rec_list

    ##
    # Update an object in the registry. Currently, this only updates the
    # PLC information associated with the record. The Geni fields (name, type,
    # GID) are fixed.
    #
    #
    #
    # @param cred credential object specifying rights of the caller
    # @param record a record object to be updated

    def update(self, cred, record, caller_cred=None):
        result = self.server.update(cred.save_to_string(save_parents=True), record.as_dict(), caller_cred)
        return result


    #-------------------------------------------------------------------------
    # Aggregate Interface
    #-------------------------------------------------------------------------
    
    ## list resources
    #
    # @param cred a credential
    # @param hrn slice hrn

    def get_resources(self, cred, hrn=None, caller_cred=None):
        result = self.server.get_resources(cred.save_to_string(save_parents=True), hrn, caller_cred)
        return result

    def get_aggregates(self, cred, hrn=None):
        result = self.server.get_aggregates(cred.save_to_string(save_parents=True), hrn)
        return result

    def get_registries(self, cred, hrn=None):
	result = self.server.get_registries(cred.save_to_string(save_parents=True), hrn)
	return result

    ## get policy
    #
    # @param cred a credential

    def get_policy(self, cred):
        result = self.server.get_policy(cred.save_to_string(save_parents=True))
        return result

    ## create slice
    #
    # @param cred a credential
    # @param rspec resource specification defining how to instantiate the slice
    
    def create_slice(self, cred, hrn, rspec, caller_cred=None):
        result = self.server.create_slice(cred.save_to_string(save_parents=True), hrn, rspec, caller_cred)
        return result


    ## delete slice
    #
    # @param cred a credential
    # @param hrn slice to delete
    def delete_slice(self, cred, hrn, caller_cred=None):
        result = self.server.delete_slice(cred.save_to_string(save_parents=True), hrn, caller_cred)
        return result    

    # ------------------------------------------------------------------------
    # Slice Interface
    # ------------------------------------------------------------------------

    ##
    # Start a slice.
    #
    # @param cred a credential identifying the caller (callerGID) and the slice
    #     (objectGID)

    def start_slice(self, cred, hrn):
        result = self.server.start_slice(cred.save_to_string(save_parents=True), hrn)
        return result

    ##
    # Stop a slice.
    #
    # @param cred a credential identifying the caller (callerGID) and the slice
    #     (objectGID)

    def stop_slice(self, cred, hrn):
        result = self.server.stop_slice(cred.save_to_string(save_parents=True), hrn)
        return result

    ##
    # Reset a slice.
    #
    # @param cred a credential identifying the caller (callerGID) and the slice
    #     (objectGID)

    def reset_slice(self, cred, hrn):
        result = self.server.reset_slice(cred.save_to_string(save_parents=True), hrn)
        return result

    ##
    # Delete a slice.
    #
    # @param cred a credential identifying the caller (callerGID) and the slice
    #     (objectGID)

    def delete_slice(self, cred, hrn, caller_cred=None):
        result = self.server.delete_slice(cred.save_to_string(save_parents=True), hrn, caller_cred)
        return result

    ##
    # List the slices on a component.
    #
    # @param cred credential object that authorizes the caller
    #
    # @return a list of slice names

    def get_slices(self, cred):
        result = self.server.get_slices(cred.save_to_string(save_parents=True))
        return result

    ##
    # Retrieve a ticket. This operation is currently implemented on the
    # registry (see SFA, engineering decisions), and is not implemented on
    # components.
    #
    # The ticket is filled in with information from the PLC database. This
    # information includes resources, and attributes such as user keys and
    # initscripts.
    #
    # @param cred credential object
    # @param name name of the slice to retrieve a ticket for
    # @param rspec resource specification dictionary
    #
    # @return a ticket object

    def get_ticket(self, cred, name, rspec):
        ticket_str = self.server.get_ticket(cred.save_to_string(save_parents=True), name, rspec)
        ticket = SfaTicket(string=ticket_str)
        return ticket

    ##
    # Redeem a ticket. This operation is currently implemented on the
    # component.
    #
    # The ticket is submitted to the node manager, and the slice is instantiated
    # or updated as appropriate.
    #
    # TODO: This operation should return a sliver credential and indicate
    # whether or not the component will accept only sliver credentials, or
    # will accept both sliver and slice credentials.
    #
    # @param ticket a ticket object containing the ticket

    def redeem_ticket(self, ticket):
        result = self.server.redeem_ticket(ticket.save_to_string(save_parents=True))
        return result


    def remove_remote_object(self, cred, hrn, record):
        result = self.server.remove_remote_object(cred.save_to_string(save_parents=True), hrn, record)
        return result
