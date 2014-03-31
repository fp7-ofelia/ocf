from foam.sfa.util.method import Method

from foam.sfa.util.parameter import Parameter

class ResolveGENI(Method):
    """
    Lookup a URN and return information about the corresponding object.
    @param urn
    """

    interfaces = ['registry']
    accepts = [
        Parameter(str, "URN"),
        Parameter(type([str]), "List of credentials"),
        ]
    returns = Parameter(bool, "Success or Failure")

    def call(self, xrn):
        return self.api.manager.Resolve(self.api, xrn, '')
