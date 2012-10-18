import abc

import amsoil.core.pluginmanager as pm
from amsoil.core import serviceinterface

AdapterBase = pm.getService('adapterbase')

class GENI2AdapterBase(AdapterBase):
    """
    Return values:
    For passing back data, each method (where an advertisement or manifest is expected) may return either a string which is returned to the user as it is.
    This string should be in RSpec3 format. The other possibility is to pass back a list of XML elements.
    
    XML Namespaces:
    TODO write this section on the rspec3_... variables

    """

    __metaclass__ = abc.ABCMeta

    rspec3_advertisement_extensions = {}
    """(Abstract) variable for RSpec schema to be sent when asked for the XML extensions for advertisements. Overwrite sending resource-specific schemas.
    The key is a string which is used for prefixing xml entries.
    E.g. {'openflow' : 'http://www.geni.net/resources/rspec/ext/openflow/3'} results in a rspec wrapper like:
    <rspec xmlns="http://www.geni.net/resources/rspec/3" xmlns:xs="http://www.w3.org/2001/XMLSchema-instance"
                 xs:schemaLocation="http://www.geni.net/resources/rspec/3 http://www.geni.net/resources/rspec/3/request.xsd http://www.geni.net/resources/rspec/ext/openflow/3"
            xmlns:openflow="http://www.geni.net/resources/rspec/ext/openflow/3"
            type="request">"""
    rspec3_request_extensions = {}
    """XML extensions for requests. See above."""

    rspec3_manifest_extensions = {}
    """XML extensions for requests. See above."""
    

    @serviceinterface
    @abc.abstractmethod
    def supportsSliverType(self, lxmlNode):
        """
        Returns True if the Adapter / ResourceManager supports the sliver type specified by {lxmlNode}.
        {lxmlNode} is a first-level part of the given RSpec in the request.
        Inherently the Adapter/ ResourceManager should be able to create such a sliver.
        lxmlNodes tag method returns the tag name with the namespace: "{...namespace...}tagname"
        Used to discriminate different adapters (e.g. for creating slivers)
        """
        return False

    @serviceinterface
    @abc.abstractmethod
    def geni2ListResources(self, **options):
        """Lists all resources.
        May be called with the following options:
          slice_urn: limit the returned resources to the slice identified by slice_urn.
          available: if given and true, only return resources which are available right now.
        
        This method shall return either an lxml node or a list of lxml nodes. This/these nodes are then appended to the result's root node.
        """
        pass

    @serviceinterface
    @abc.abstractmethod
    def geni2CreateSliver(self, sliceURN, lxmlRSpecPart, fullRequestRspec, users, **options):
        """Creates a sliver.
        Credentials are in the request context.
        See 
        """
        pass
    
    @serviceinterface
    @abc.abstractmethod
    def geni2DeleteSliver(self, sliceURN, **options):
        """
        Receives the request to remove all slivers in the given {sliceURN}.
        This method shall return True if all attached adapter/resource manager be deleted or there were none otherwise False.
        """
        pass
    
    @serviceinterface
    @abc.abstractmethod
    def geni2SliverStatus(self, sliceURN, **options):
        """Get the status of all slivers in in the given {sliceURN}.
        This method shall return a list of dicts in the following form (stupid GENI API, see http://groups.geni.net/geni/wiki/GAPI_AM_API_V2_DETAILS#Return4):
            { geni_urn: <resource URN>
              geni_status: ready
              geni_error: ''}
        If the adapter/resource manager attached does not have any resources, this method may return []."""
        pass
        
    @serviceinterface
    @abc.abstractmethod
    def geni2RenewSliver(self, sliceURN, exparationTime, **options):
        """Extend the exparation time of all  slivers in the given {sliceURN}.
        This method shall return True if all attached adapter/resource manager could extend the exparation time otherwise False."""
        pass
        
    @serviceinterface
    @abc.abstractmethod
    def geni2Shutdown(self, sliceURN, **options):
        """Perform an emergency shutdown of all slivers in the given {sliceURN}.
        This method shall return True if all attached adapter/resource manager shutdown the slivers otherwise False."""
        pass
        
        
        
        
    