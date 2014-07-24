'''Contains the functionality of the GENI Clearinghouse.

Much of this code is from the GCF library distributed by BBN. Below is
their copyright.

Created on Oct 2, 2010

@author: jnaous
'''

#----------------------------------------------------------------------
# Copyright (c) 2010 Raytheon BBN Technologies
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and/or hardware specification (the "Work") to
# deal in the Work without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Work, and to permit persons to whom the Work
# is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Work.
#
# THE WORK IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE WORK OR THE USE OR OTHER DEALINGS
# IN THE WORK.
#----------------------------------------------------------------------

import logging
from expedient.common.federation.geni.util.urn_util import URN
from expedient.clearinghouse.geni.utils import get_slice_urn, create_x509_cert,\
    create_slice_credential, create_user_credential, create_slice_urn
import traceback
from expedient.common.federation.sfa.trust import gid
from expedient.clearinghouse.geni.backends import get_username_from_cert
from django.contrib.auth.models import User

logger = logging.getLogger("geni.clearinghouse")

class BadURNException(Exception):
    """Raised if the URN is not one the CH would generate."""
    pass

def GetVersion():
    return {"geni_api": 1}

def CreateSlice(user_cert, urn_req=None):
    
    # Is this user allowed to create a slice?
    # first get the user with this cert
    username = get_username_from_cert(user_cert)
    try:
        User.objects.get(username=username)
    except User.DoesNotExist:
        raise Exception("Unknown user %s." % username)
    
    if urn_req:
        # check the requested URN
        urn = URN(urn=urn_req)
        
        # make sure that we would generate the same urn if using the
        # same name (i.e. authority is the same...)
        urn_gen = get_slice_urn(urn.getName())
        
        if urn_gen != urn_req:
            raise BadURNException(
                "The requested URN is not one that would be generated"
                " by this clearinghouse. Requested was %s, but generated"
                " is %s" % (urn_req, urn_gen)
            )
            
    else:
        # Generate a unique URN for the slice
        urn_req = create_slice_urn()
        
    try:
        slice_gid = create_x509_cert(urn_req)[0]
    except Exception as exc:
        logger.error("Could not create slice. Error\n %s"
                     % traceback.format_exc())
        raise Exception("Failed to create slice %s." % urn_req)

    # Now get the user GID which will have permissions on this slice.
    # It doesnt have the chain but should be signed
    # by this CHs cert, which should also be a trusted
    # root at any federated AM. So everyone can verify it as is.
    # Note that if a user from a different CH (installed
    # as trusted by this CH for some reason) called this method,
    # that user would be used here - and can still get a valid slice
    try:
        user_gid = gid.GID(string=user_cert)
    except Exception, exc:
        logger.error("CreateSlice failed to create user_gid from SSL client cert: %s", traceback.format_exc())
        raise Exception("Failed to create slice %s. Cant get user GID from SSL client certificate." % urn_req, exc)

    # OK have a user_gid so can get a slice credential
    # authorizing this user on the slice
    try:
        slice_cred = create_slice_credential(user_gid, slice_gid)
    except Exception, exc:
        logger.error('CreateSlice failed to get slice credential for user %r, slice %r: %s', user_gid.get_hrn(), slice_gid.get_hrn(), traceback.format_exc())
        raise Exception('CreateSlice failed to get slice credential for user %r, slice %r' % (user_gid.get_hrn(), slice_gid.get_hrn()), exc)
    logger.info('Created slice %r' % (urn_req))
    
    return slice_cred.save_to_string()

def DeleteSlice(urn_req):
    logger.info("Called DeleteSlice %r" % urn_req)
    return True

def ListAggregates():
    logger.info("Called ListAggregates")
    # FIXME: return the GCF aggregates registered here
    return []

def CreateUserCredential(user_gid):
    '''Return string representation of a user credential
    issued by this CH with caller/object this user_gid (string)
    with user privileges'''

    username = get_username_from_cert(user_gid)
    try:
        User.objects.get(username=username)
    except User.DoesNotExist:
        raise Exception("Unknown user %s." % username)

    user_gid = gid.GID(string=user_gid)
    logger.info("Called CreateUserCredential for GID %s" % user_gid.get_hrn())
    try:
        ucred = create_user_credential(user_gid)
    except Exception, exc:
        logger.error("Failed to create user credential for %s: %s", user_gid.get_hrn(), traceback.format_exc())
        raise Exception("Failed to create user credential for %s" % user_gid.get_hrn(), exc)
    return ucred.save_to_string()
