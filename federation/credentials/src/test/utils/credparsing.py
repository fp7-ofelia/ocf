#!/usr/bin/python

#----------------------------------------------------------------------
# Copyright (c) 2011 Raytheon BBN Technologies
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
"""
   Utilities to parse credentials
"""

import datetime
import dateutil.parser
import logging
import traceback
import xml.dom.minidom as md

# FIXME: Doesn't distinguish v2 vs v3 yet
def is_valid_v3(logger, credString):
    '''Is the given credential a valid geni_sfa style v3 credential?'''
    if not logger:
        logger = logging.getLogger("omnilib.credparsing")

    if not credString:
        logger.warn("None credString - not geni_sfa v3")
        return False
    if not isinstance(credString, str):
        logger.warn("Not string credString %s", credString)
        return False
    if credString.strip() == "":
        logger.warn("Empty string cred")
        return False

    if credString.startswith("-----BEGIN CERTIFICATE"):
        logger.warn("Cred seems to be a certificate: %s", credString)
        return False

    if not credString.startswith("<?xml"):
        logger.warn("No ?xml to start cred: %s", credString)
        return False
    if not "signed-credential" in credString:
        logger.warn("No signed-credential in cred: %s", credString)
        return False
    if not "owner_gid" in credString:
        logger.warn("No owner_gid in cred: %s", credString)
        return False
    if not "target_gid" in credString:
        logger.warn("No target_gid in cred: %s", credString)
        return False
    if not "Signature" in credString:
        logger.warn("No Signature in cred: %s", credString)
        return False

    try:
        doc = md.parseString(credString)
        signed_cred = doc.getElementsByTagName("signed-credential")

        # Is this a signed-cred or just a cred?
        if len(signed_cred) > 0:
            cred = signed_cred[0].getElementsByTagName("credential")[0]
        else:
            logger.warn("No signed-credential element found")
            return False

        targetnode = cred.getElementsByTagName("target_urn")[0]
        if len(targetnode.childNodes) > 0:
            urn = str(targetnode.childNodes[0].nodeValue)
        else:
            logger.warn("No target_urn found")
            return False
    except Exception, exc:
        logger.warn("Exception parsing cred to get target_urn: %s", exc)
        return False

# Want to rule out ABAC
# Want to rule out geni_sfa v2 if possible

# 1) Call:
#    sfa.trust.credential.cred.verify(trusted_certs=None, schema=FIXME, trusted_certs_required=False)
    # Will have to check in the xsd I think

# 2)
    # also for each cert:
    #   retrieve gid from cred
    #   check not expired
    #   check version is 3
    #   get email, urn, uuid - all not empty
    #   more? CA:TRUE/FALSE? real serialNum? Has a DN?
    #    if type is slice or user, CA:FALSE. It type is authority, CA:TRUE
    #   Should this be in gid.py? or in geni.util.cert_util?
    #

    return True

def get_cred_target_urn(logger, cred):
    '''Parse the given credential to get its target URN'''
    credString = get_cred_xml(cred)
    urn = ""

    if credString is None:
        return urn

    # If credString is not a string then complain and return
    if type(credString) != type('abc'):
        if logger is None:
            level = logging.INFO
            logging.basicConfig(level=level)
            logger = logging.getLogger("omni.credparsing")
            logger.setLevel(level)
        logger.error("Cannot parse target URN: Credential is not a string: %s", str(credString))
        return cred

    try:
        doc = md.parseString(credString)
        signed_cred = doc.getElementsByTagName("signed-credential")

        # Is this a signed-cred or just a cred?
        if len(signed_cred) > 0:
            cred = signed_cred[0].getElementsByTagName("credential")[0]
        else:
            cred = doc.getElementsByTagName("credential")[0]

        targetnode = cred.getElementsByTagName("target_urn")[0]
        if len(targetnode.childNodes) > 0:
            urn = str(targetnode.childNodes[0].nodeValue)
        else:
            if logger is None:
                level = logging.INFO
                logging.basicConfig(level=level)
                logger = logging.getLogger("omni.credparsing")
                logger.setLevel(level)
            logger.warn("Found no targetnode to get target_urn?")
    except Exception, exc:
        if logger is None:
            level = logging.INFO
            logging.basicConfig(level=level)
            logger = logging.getLogger("omni.credparsing")
            logger.setLevel(level)
        logger.error("Failed to parse credential for target URN: %s", exc)
        logger.info("Unparsable credential: %s", credString)
        logger.debug(traceback.format_exc())

    return urn

def get_cred_exp(logger, cred):
    '''Parse the given credential in GENI AM API XML format to get its expiration time and return that'''

    # Don't fully parse credential: grab the expiration from the string directly
    credexp = datetime.datetime.fromordinal(1)

    credString = get_cred_xml(cred)

    if credString is None:
        # failed to get a credential string. Can't check
        return credexp

    # If credString is not a string then complain and return
    if type(credString) != type('abc'):
        if logger is None:
            level = logging.INFO
            logging.basicConfig(level=level)
            logger = logging.getLogger("omni.credparsing")
            logger.setLevel(level)
        logger.error("Cannot parse expiration date: Credential is not a string: %s", str(credString))
        return credexp

    try:
        doc = md.parseString(credString)
        signed_cred = doc.getElementsByTagName("signed-credential")

        # Is this a signed-cred or just a cred?
        if len(signed_cred) > 0:
            cred = signed_cred[0].getElementsByTagName("credential")[0]
        else:
            cred = doc.getElementsByTagName("credential")[0]
        expirnode = cred.getElementsByTagName("expires")[0]
        if len(expirnode.childNodes) > 0:
            credexp = dateutil.parser.parse(expirnode.childNodes[0].nodeValue)
    except Exception, exc:
        if logger is None:
            level = logging.INFO
            logging.basicConfig(level=level)
            logger = logging.getLogger("omni.credparsing")
            logger.setLevel(level)
        logger.error("Failed to parse credential for expiration time: %s", exc)
        logger.info("Unparsable credential: %s", credString)
        logger.debug(traceback.format_exc())

    return credexp

def is_cred_xml(cred):
    '''Is this a cred in XML format, or a struct? Return true if XML'''
    if cred is None:
        return False
    if not isinstance(cred, str):
        return False
    if cred.strip() == "":
        return False
    cred = cred.strip()
    if not cred.startswith("<?xml"):
        return False
    if not "signed-credential" in cred:
        return False

    try:
        doc = md.parseString(cred)
        signed_cred = doc.getElementsByTagName("signed-credential")

        # Is this a signed-cred or just a cred?
        if len(signed_cred) > 0:
            credEle = signed_cred[0].getElementsByTagName("credential")[0]
        else:
            return False

        targetnode = credEle.getElementsByTagName("target_urn")[0]
        if len(targetnode.childNodes) > 0:
            urn = str(targetnode.childNodes[0].nodeValue)
        else:
            return False
    except Exception, exc:
        return False

    # Anything else? Starts with <?
    return True

def get_cred_xml(cred):
    '''Return the cred XML, from the struct if any, else None'''
    if is_cred_xml(cred):
        return cred
    # Make sure the cred is the right struct?
    # extract the real cred
#        {
#           geni_type: <string>,
#           geni_version: <string>,
#           geni_value: <the credential as a string>
#        }

    if isinstance(cred, dict) and cred.has_key("geni_value"):
        return cred["geni_value"]

    return None

