'''
Created on Jul 19, 2010

@author: jnaous
'''

# super user name into the local CH and OM
SUPERUSER_USERNAME = "expedient"
SUPERUSER_PASSWORD = "expedient"

# Local Flowvisor info
FV_USERNAME = "root"
FV_PASSWORD = "rootpassword"
FV_URL = "https://171.67.75.9:8080/xmlrpc/"

# Username/password Expedient should use to contact local OM
CH_USERNAME = "ch_user"
CH_PASSWORD = "password"

# Users registered locally at Expedient and at the OM.
# dict of dicts keyed by username. Values are dicts with keys "password",
# "email", "flowspace", "opt_to_slices", "projects", "ch_slices"
# flowspace: is a list of dicts with the following keys: "mac_addr" and
#            "ip_addr". These can either be "*" or an actual mac/ip address.
# "opt_to_slices": list of slices to opt into by name.
# "projects": list of dicts describing projects to create. Each has keys:
#        "name", "description", "slices"
#         "slices" is a list of slices to create. List of dicts, each with
#         keys: "name", "description"
USER_INFO = {
    "demo_user": {
        "password": "password",
        "email": "email@email.com",
        "flowspace": {
            "10.79.1.90": "00:14:D1:19:43:ED",
            "10.79.1.91": "00:14:D1:19:43:F4",
            "10.79.1.51": "A4:BA:DB:21:E0:70",
            "10.79.1.53": "A4:BA:DB:2B:DA:CE",
            "10.79.1.52": "A4:BA:DB:2B:DB:2D",
        },
        "opt_to_slices": [
            "Demo Slice",
        ],
        "projects": [
            dict(
                name="Demo Project",
                description="This is the demo project",
                slices=[
                    dict(
                        name="Demo Slice",
                        description="This is the demo slice",
                    ),
                ]
            ),
        ],
    },
}

# List of dicts describing planetlab aggregates. Keys are:
# "name", "description", "location", "url"
PL_AGGREGATE_INFO = [
    {
        "name": "MyPLC at Stanford",
        "description": "Stanford's MyPLC deployment.",
        "location": "Stanford, CA",
        "url": "https://nfcm13.stanford.edu:12348",
    },
    {
        "name": "MyPLC at BBN's GPO labs",
        "description": "BBN's MyPLC deployment.",
        "location": "Cambridge, MA",
        "url": "https://myplc4.gpolab.bbn.com:12348",
    },
    # {
    #     "name": "MyPLC at University of Washington",
    #     "description": "U.W. MyPLC deployment.",
    #     "location": "Seattle, WA",
    #     "url": "http://myplc.grnoc.iu.edu:12348",
    # },
]

# list of dicts describing OpenFlow aggregates. Keys are:
# "name", "description", "location", "usage_agreement", "username", "password",
# "url"
OF_AGGREGATE_INFO = [
    # {
    #     "name": "Stanford OpenFlow Network",
    #     "description": "Stanford's OpenFlow deployment on the production network.",
    #     "location": "Stanford, CA",
    #     "usage_agreement": "Do you agree?",
    #     "username": CH_USERNAME,
    #     "password": CH_PASSWORD,
    #     "url": "https://openflow4.stanford.edu:8443/xmlrpc/xmlrpc/",
    # },
    {
        "name": "BBN OpenFlow Network",
        "description": "BBN's OpenFlow deployment in GPO Labs.",
        "location": "Cambridge, MA",
        "usage_agreement": "Do you agree?",
        "username": "uruk_ch",
        "password": "demo",
        "url": "https://uruk.gpolab.bbn.com:8443/xmlrpc/xmlrpc/",
    },
]

# list of connections from dpid:port to planetlab hostnames. Format
# is a tuple (dpid, port_num, node hostname)
OF_PL_CONNECTIONS = [
    ("00:00:00:12:e2:98:a5:d0", 4, "of-planet1.stanford.edu"),
    ("00:00:00:12:e2:78:67:65", 4, "of-planet2.stanford.edu"),
    ("00:00:e2:b8:dc:3b:17:94", 3, "sardis.gpolab.bbn.com"),
    ("00:00:e2:b8:dc:3b:17:91", 1, "ganel.gpolab.bbn.com"),
    ("00:00:e2:b8:dc:3b:17:95", 1, "gardil.gpolab.bbn.com"),
]
