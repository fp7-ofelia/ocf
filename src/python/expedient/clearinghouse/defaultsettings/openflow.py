'''Settings for the OpenFlow plugin.

Created on Aug 19, 2010

@author: jnaous
'''

# Settings for the GENI API interface
OPENFLOW_GAPI_RSC_URN_PREFIX = "urn:publicid:IDN+expedient:stanford:openflow"
'''The prefix appended to the URN of OpenFlow resources exposed through the GENI-API.

You will need to override this for your particular deployment (mainly by
replacing "stanford" with your site's name.

'''

OPENFLOW_GAPI_AM_URN = "urn:publicid:IDN+expedient:stanford:openflow+am+authority"
'''The URN used as the name of the OpenFlow Aggregate Manager.

You will need to override this for your particular deployment (mainly by
replacing "stanford" with your site's name.

'''

OPENFLOW_OTHER_RESOURCES = (
    ("geni.planetlab", "PlanetLabNode"),
)
'''Which types of non-OpenFlow resources do OpenFlow Interface connect to?

This is a list of two-tuples: (application module name, resource class name)

''' 

OPENFLOW_GAPI_FILTERED_AGGS = []
'''List of OpenFlow Aggregates that you do not want to show or use in the GAPI interface.

This should be a list of the *names* of the aggregates that you do not want
to be shown in the ListResource GENI-API call.

'''
