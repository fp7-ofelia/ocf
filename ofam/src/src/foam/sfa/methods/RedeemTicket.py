from foam.sfa.util.method import Method

from foam.sfa.util.parameter import Parameter, Mixed

class RedeemTicket(Method):
    """

    @param cred credential string specifying the rights of the caller
    @param ticket 
    @return 1 is successful, faults otherwise  
    """

    interfaces = ['component']
    
    accepts = [
        Parameter(str, "Ticket  string representation of SFA ticket"),
        Mixed(Parameter(str, "Credential string"),
              Parameter(type([str]), "List of credentials")),
        ]

    returns = [Parameter(int, "1 if successful")]
    
    def call(self, ticket, creds):
        valid_creds = self.api.auth.checkCredentials(cred, 'redeemticket')
        self.api.auth.check_ticket(ticket)

        # send the call to the right manager
        self.api.manager.redeem_ticket(self.api, ticket) 
        return 1 
