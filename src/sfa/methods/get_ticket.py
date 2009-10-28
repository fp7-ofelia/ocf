### $Id: get_ticket.py 14306 2009-07-06 20:38:44Z thierry $
### $URL: http://svn.planet-lab.org/svn/sfa/trunk/sfa/methods/get_ticket.py $

from sfa.util.faults import *
from sfa.util.method import Method
from sfa.util.parameter import Parameter, Mixed
from sfa.trust.auth import Auth
from sfa.util.sfaticket import SfaTicket

class get_ticket(Method):
    """
    Retrieve a ticket. This operation is currently implemented on PLC
    only (see SFA, engineering decisions); it is not implemented on
    components.
    
    The ticket is filled in with information from the PLC database. This
    information includes resources, and attributes such as user keys and
    initscripts.
    
    @param cred credential string
    @param name name of the slice to retrieve a ticket for
    @param rspec resource specification dictionary
    
    @return the string representation of a ticket object
    """

    interfaces = ['registry']
    
    accepts = [
        Parameter(str, "Credential string"),
        Parameter(str, "Human readable name of slice to retrive a ticket for (hrn)"),
        Parameter(str, "Resource specification (rspec)")
        ]

    returns = Parameter(str, "String represeneation of a ticket object")
    
    def call(self, cred, hrn, rspec):
        self.api.auth.check(cred, "getticket")
        self.api.auth.verify_object_belongs_to_me(hrn)
        self.api.auth.verify_object_permission(name)

        # XXX much of this code looks like get_credential... are they so similar
        # that they should be combined?

        auth_hrn = self.api.auth.get_authority(hrn)
        if not auth_hrn:
            auth_hrn = hrn
        auth_info = self.api.auth.get_auth_info(auth_hrn)
        record = None
        table = self.api.auth.get_auth_table(auth_hrn)
        record = table.resolve('slice', hrn)

        object_gid = record.get_gid_object()
        new_ticket = SfaTicket(subject = object_gid.get_subject())
        new_ticket.set_gid_caller(self.client_gid)
        new_ticket.set_gid_object(object_gid)
        new_ticket.set_issuer(key=auth_info.get_pkey_object(), subject=auth_hrn)
        new_ticket.set_pubkey(object_gid.get_pubkey())

        self.api.fill_record_info(record)

        (attributes, rspec) = self.api.record_to_slice_info(record)

        new_ticket.set_attributes(attributes)
        new_ticket.set_rspec(rspec)

        new_ticket.set_parent(self.api.auth.hierarchy.get_auth_ticket(auth_hrn))

        new_ticket.encode()
        new_ticket.sign()

        return new_ticket.save_to_string(save_parents=True)
        
