# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University

from __future__ import absolute_import

import logging

from flask import request
import geni
import sfa

from foam.core.configdb import ConfigDB
from foam.core.exception import CoreException

flog = logging.getLogger('foam')

class Certificate(object):
  def __init__ (self, pemstr):
    self.cert = sfa.trust.certificate.Certificate(string=pemstr)
    self.email = None
    self.uri = None

    self._parseData()

  def _parseData (self):
    san = self.cert.get_data('subjectAltName')
    for elem in san.split(','):
      (key, val) = elem.split(':', 1)
      key = key.strip()
      if key == 'email':
        self.email = val
      elif key == 'URI':
        self.uri = val
      else:
        flog.debug("[Cert] Unparsed cert key <%s>" % (key))

  def getEmailAddress (self):
    return self.email

  def getURN (self):
    return self.uri
    
class TokenError(CoreException):
  def __init__ (self, err):
    self.err = err
  def __str__ (self):
    return self.err
    
class _CredVerifier(object):
  def __init__ (self):
    self._cred_verifier = geni.CredentialVerifier(ConfigDB.getConfigItemByKey("geni.cert-dir").getValue())

  def fromStrings (self, creds, privs, slice_urn):
    if not request.environ.has_key('CLIENT_RAW_CERT'):
      # Using dev server
      return []

    if isinstance(privs, str):
      privs = [privs]
    return self._cred_verifier.verify_from_strings(request.environ['CLIENT_RAW_CERT'], creds, slice_urn, privs)

  def checkValid (self, creds, privs, slice_urn=None):
    if not request.environ.has_key('CLIENT_RAW_CERT'):
      # Using dev server
      return True

    if isinstance(privs, str):
      privs = [privs]
    self._cred_verifier.verify_from_strings(request.environ['CLIENT_RAW_CERT'], creds, slice_urn, privs)
    return True

class _TokenVerifier(object):
  def __init__ (self):
    pass

  def checkToken (self, priv, sliver):
    if priv == "approve-sliver":
      return True
    elif priv == "expire-sliver":
      return True
    else:
      raise TokenError("Invalid Token: %s, %s" % (priv, sliver))

CredVerifier = _CredVerifier()
TokenVerifier = _TokenVerifier()
