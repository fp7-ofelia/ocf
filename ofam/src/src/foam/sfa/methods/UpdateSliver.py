from foam.sfa.util.parameter import Parameter, Mixed

from foam.sfa.methods.CreateSliver import CreateSliver

class UpdateSliver(CreateSliver):
    """
    Allocate resources to a slice.  This operation is expected to
    start the allocated resources asynchornously after the operation
    has successfully completed.  Callers can check on the status of
    the resources using SliverStatus.

    @param slice_urn (string) URN of slice to allocate to
    @param credentials ([string]) of credentials
    @param rspec (string) rspec to allocate
    
    """
    interfaces = ['aggregate', 'slicemgr']
    accepts = [
        Parameter(str, "Slice URN"),
        Mixed(Parameter(str, "Credential string"),
              Parameter(type([str]), "List of credentials")),
        Parameter(str, "RSpec"),
        Parameter(type([]), "List of user information"),
        Parameter(dict, "options"),
        ]
    returns = Parameter(str, "Allocated RSpec")



    def call(self, slice_xrn, creds, rspec, users, options):

        return CreateSliver.call(self, slice_xrn, creds, rspec, users, options)
    
