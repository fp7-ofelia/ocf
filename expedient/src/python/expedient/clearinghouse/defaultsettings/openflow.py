'''Settings for the OpenFlow plugin.

Created on Aug 19, 2010

@author: jnaous
'''

# Settings for the GENI API interface
OPENFLOW_GCF_BASE_SUFFIX = "openflow"
'''The suffix appended to the URN of OpenFlow resources exposed through the GENI-API.

This gets concatenated with 
L{expedient.clearinghouse.defaultsettings.gcf.GCF_BASE_NAME} to produce
the full HRN used for the URNs. Default is "openflow".

'''

OPENFLOW_OTHER_RESOURCES = (
    ("expedient.clearinghouse.geni.planetlab", "PlanetLabNode"),
)
'''Which types of non-OpenFlow resources do OpenFlow Interface connect to?

This is a list of two-tuples: (application module name, resource class name)

''' 

OPENFLOW_GAPI_FILTERED_AGGS = []
'''List of OpenFlow Aggregates that you do not want to show or use in the GAPI interface.

This should be a list of the *names* of the aggregates that you do not want
to be shown in the ListResource GENI-API call.

'''

OPENFLOW_TOPOLOGY_UPDATE_PERIOD = 5*60
'''Every how many seconds should an OpenFlow Aggregate update its topology?

'''
