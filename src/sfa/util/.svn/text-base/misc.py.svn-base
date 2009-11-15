### $Id$
### $URL$

from sfa.util.faults import *

def get_leaf(hrn):
    parts = hrn.split(".")
    return ".".join(parts[-1:])

def get_authority(hrn):
    parts = hrn.split(".")
    return ".".join(parts[:-1])

def hrn_to_pl_slicename(hrn):
    parts = hrn.split(".")
    return parts[-2] + "_" + parts[-1]

# assuming hrn is the hrn of an authority, return the plc authority name
def hrn_to_pl_authname(hrn):
    parts = hrn.split(".")
    return parts[-1]

# assuming hrn is the hrn of an authority, return the plc login_base
def hrn_to_pl_login_base(hrn):
    return hrn_to_pl_authname(hrn)

def hostname_to_hrn(auth_hrn, login_base, hostname):
    """
    Convert hrn to plantelab name.
    """
    genihostname = ".".join([auth_hrn, login_base, hostname.split(".")[0]])
    return genihostname

def slicename_to_hrn(auth_hrn, slicename):
    """
    Convert hrn to planetlab name.
    """
    parts = slicename.split("_")
    slice_hrn = ".".join([auth_hrn, parts[0]]) + "." + "_".join(parts[1:])

    return slice_hrn

def email_to_hrn(auth_hrn, email):
    parts = email.split("@")
    username = parts[0]
    username = username.replace(".", "_") 
    person_hrn = ".".join([auth_hrn, username])
    
    return person_hrn 
