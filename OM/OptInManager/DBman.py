# tools for working with flow space
from OM.OptInManager.models import Profile, Admin, User

def addProfile(isid, ipassword, iname, iemail, iphone):
    #check for uniqueness of system id (sid)
    p = Profile(sid=isid, password=ipassword, name=iname, email=iemail, phone=iphone)
    return true

def requestUserFSRegister(isid, ivlan, iip_src):
    #find the lowest-level admin responsible for this request

    #check overlap with other similar level reservations
    
    #call the auth function for admin if there is any (pay attention to security issue)
    # and return the result of that call
    # if there is no auth function, just add the request to pending user requests
    # for that admin, so that he can approve it next time he logs in
    return true

def requestAdminFSRegister(isid, ivlan_s, ivlan_e, iip_src_s, iip_src_e, ipriority):
    #find all admins whose FS are superset of requested FS among them select the
    # one with lowest priority (highest priority number).
    # Also check that it is disjoint from all the others

    # assign the maximum of requested ipririty and the found admin prioirty+1 as
    # priority.

    # Add the request to request database.
    return true


def dropUser(isid):
    return true


def isOverlaped(user_sid1, user_sid2):
    return true

def isIsolated(user_sid1, user_sid2):
    return true