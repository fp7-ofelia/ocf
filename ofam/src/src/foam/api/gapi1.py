# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University
# Copyright (c) 2012  Barnstormer Softworks, Ltd.

import logging
import zlib
import base64
import xmlrpclib
from xml.parsers.expat import ExpatError

from flaskext.xmlrpc import XMLRPCHandler, Fault
from flask import request

import foam.task
import foam.lib
import foam.api.xmlrpc
import foam.version
import foam.geni.approval
from foam.creds import CredVerifier, Certificate
from foam.config import AUTO_SLIVER_PRIORITY, GAPI_REPORTFOAMVERSION
from foam.core.configdb import ConfigDB
from foam.core.log import KeyAdapter
from foam.geni.db import GeniDB, UnknownSlice, UnknownNode

import foam.geni.lib

import sfa


class AMAPIv1(foam.api.xmlrpc.Dispatcher):
  def __init__ (self, log):
    super(AMAPIv1, self).__init__("GAPIv1", log)
    self._actionLog = KeyAdapter("v1", logging.getLogger('gapi-actions'))

  def recordAction (self, action, credentials = [], urn = None):
    cred_ids = []

    self._actionLog.info("Sliver: %s  Action: %s" % (urn, action))

    for cred in credentials:
      self._actionLog.info("Credential: %s" % (cred))

  def pub_GetVersion (self):
    self.recordAction("getversion")
    d = {"geni_api" : 1,
         "request_rspec_versions" : [
            { 'extensions': [ 'http://www.geni.net/resources/rspec/ext/openflow/3',
                              'http://www.geni.net/resources/rspec/ext/openflow/4',
                              'http://www.geni.net/resources/rspec/ext/flowvisor/1', ],
               'namespace': 'http://www.geni.net/resources/rspec/3',
               'schema': 'http://www.geni.net/resources/rspec/3/request.xsd',
               'type': 'GENI',
               'version': '3'}
            ],
         "ad_rspec_versions" : [
            { 'extensions': [ 'http://www.geni.net/resources/rspec/ext/openflow/3' ],
              'namespace': 'http://www.geni.net/resources/rspec/3',
              'schema': 'http://www.geni.net/resources/rspec/3/ad.xsd',
              'type': 'GENI',
              'version': '3'}
            ],
         }
    if GAPI_REPORTFOAMVERSION:
      d["foam_version"] = foam.version.VERSION
    d["site_info"] = self.generateSiteInfo()

    return d

  def generateSiteInfo (self):
    dmap = [("site.admin.name", "admin-name"),
            ("site.admin.email", "admin-email"),
            ("site.admin.phone", "admin-phone"),
            ("site.location.address", "org-address"),
            ("site.location.organization", "org-name"),
            ("site.description", "description")]

    sinfo = {}
    for ckey, vkey in dmap:
      val = ConfigDB.getConfigItemByKey(ckey).getValue()
      if val is not None:
        sinfo[vkey] = val

    return sinfo

  def pub_ListResources (self, credentials, options):
    try:
      CredVerifier.checkValid(credentials, [])

      compressed = options.get("geni_compressed", False)
      urn = options.get("geni_slice_urn", None)

      if urn:
        CredVerifier.checkValid(credentials, "getsliceresources", urn)
        self.recordAction("listresources", credentials, urn)
        sliver_urn = GeniDB.getSliverURN(urn)
        if sliver_urn is None:
          raise Fault("ListResources", "Sliver for slice URN (%s) does not exist" % (urn))
        rspec = GeniDB.getManifest(sliver_urn)
      else:
        self.recordAction("listresources", credentials)
        rspec = foam.geni.lib.getAdvertisement()
      if compressed:
        zrspec = zlib.compress(rspec)
        rspec = base64.b64encode(zrspec)

      return rspec
    except ExpatError, e:
      self._log.error("Error parsing credential strings")
      e._foam_logged = True
      raise e
    except UnknownSlice, x:
      x.log(self._log, "Attempt to list resources on sliver for unknown slice %s" % (urn),
            logging.INFO)
      x._foam_logged = True
      raise x
    except xmlrpclib.Fault, x:
      # Something thrown via GCF, we'll presume it was something related to credentials
      self._log.info("GCF credential check failure.")
      self._log.debug(x, exc_info=True)
      x._foam_logged = True
      raise x
    except Exception, e:
      self._log.exception("Exception")
      raise e

  def pub_CreateSliver (self, slice_urn, credentials, rspec, users):
    user_info = {}
    try:
      if CredVerifier.checkValid(credentials, "createsliver"):
        self.recordAction("createsliver", credentials, slice_urn)
        try:
          cert = Certificate(request.environ['CLIENT_RAW_CERT'])
          user_info["urn"] = cert.getURN()
          user_info["email"] = cert.getEmailAddress()
          self._log.debug("Parsed user cert with URN (%(urn)s) and email (%(email)s)" % user_info)
        except Exception, e:
          self._log.exception("UNFILTERED EXCEPTION")
          user_info["urn"] = None
          user_info["email"] = None
        sliver = foam.geni.lib.createSliver(slice_urn, credentials, rspec, user_info)

        approve = foam.geni.approval.analyzeForApproval(sliver)
        style = ConfigDB.getConfigItemByKey("geni.approval.approve-on-creation").getValue()
        if style == foam.geni.approval.NEVER:
          approve = False
        elif style == foam.geni.approval.ALWAYS:
          approve = True
        if approve:
          pid = foam.task.approveSliver(sliver.getURN(), AUTO_SLIVER_PRIORITY)
          self._log.debug("task.py launched for approve-sliver (PID: %d)" % pid)

        data = GeniDB.getSliverData(sliver.getURN(), True)
        foam.task.emailCreateSliver(data)

        return GeniDB.getManifest(sliver.getURN())
      return
    except foam.geni.lib.RspecParseError, e:
      self._log.info(str(e))
      e._foam_logged = True
      raise e
    except foam.geni.lib.RspecValidationError, e:
      self._log.info(str(e))
      e._foam_logged = True
      raise e
    except foam.geni.lib.DuplicateSliver, ds:
      self._log.info("Attempt to create multiple slivers for slice [%s]" % (ds.slice_urn))
      ds._foam_logged = True
      raise ds
    except foam.geni.lib.UnknownComponentManagerID, ucm:
      raise Fault("UnknownComponentManager", "Component Manager ID specified in %s does not match this aggregate." % (ucm.cid))
    except (foam.geni.lib.UnmanagedComponent, UnknownNode), uc:
      self._log.info("Attempt to request unknown component %s" % (uc.cid))
      f = Fault("UnmanagedComponent", "DPID in component %s is unknown to this aggregate." % (uc.cid))
      f._foam_logged = True
      raise f
    except Exception, e:
      self._log.exception("Exception")
      raise e

  def pub_DeleteSliver (self, slice_urn, credentials):
    try:
      if CredVerifier.checkValid(credentials, "deletesliver", slice_urn):
        self.recordAction("deletesliver", credentials, slice_urn)
        if GeniDB.getSliverURN(slice_urn) is None:
          raise Fault("DeleteSliver", "Sliver for slice URN (%s) does not exist" % (slice_urn))

        sliver_urn = GeniDB.getSliverURN(slice_urn)
        data = GeniDB.getSliverData(sliver_urn, True)

        foam.geni.lib.deleteSliver(sliver_urn = sliver_urn)

        foam.task.emailGAPIDeleteSliver(data)

        return True
      return False
    except UnknownSlice, x:
      self._log.info("Attempt to delete unknown sliver for slice URN %s" % (slice_urn))
      x._foam_logged = True
      raise x
    except Exception, e:
      self._log.exception("Exception")
      raise e

  def pub_SliverStatus (self, slice_urn, credentials):
    try:
      if CredVerifier.checkValid(credentials, "sliverstatus", slice_urn):
        self.recordAction("sliverstatus", credentials, slice_urn)
        result = {}
        sliver_urn = GeniDB.getSliverURN(slice_urn)
        if not sliver_urn:
          raise Fault("SliverStatus", "Sliver for slice URN (%s) does not exist" % (slice_urn))
        sdata = GeniDB.getSliverData(sliver_urn, True)
        status = foam.geni.lib.getSliverStatus(sliver_urn)
        result["geni_urn"] = sliver_urn
        result["geni_status"] = status
        result["geni_resources"] = [{"geni_urn" : sliver_urn, "geni_status": status, "geni_error" : ""}]
        result["foam_status"] = sdata["status"]
        result["foam_expires"] = sdata["expiration"]
        result["foam_pend_reason"] = sdata["pend_reason"]
        return result
      return False
    except UnknownSlice, x:
      self._log.info("Attempt to get status on unknown sliver for slice %s" % (slice_urn))
      x._foam_logged = True
      raise x
    except Exception, e:
      self._log.exception("Exception")
      raise e

  def pub_RenewSliver (self, slice_urn, credentials, exptime):
    try:
      if CredVerifier.checkValid(credentials, "renewsliver", slice_urn):
        self.recordAction("renewsliver", credentials, slice_urn)
        creds = CredVerifier.fromStrings(credentials, "renewsliver", slice_urn)
        sliver_urn = foam.lib.renewSliver(slice_urn, creds, exptime)

        data = GeniDB.getSliverData(sliver_urn, True)
        foam.task.emailRenewSliver(data)

        return True
      return False
    except foam.lib.BadSliverExpiration, e:
      self._log.info("Bad expiration request: %s" % (e.msg))
      e._foam_logged = True
      raise e
    except Exception, e:
      self._log.exception("Exception")
      raise e

  def pub_Shutdown (self, slice_urn, credentials):
    if CredVerifier.checkValid(credentials, "shutdown", slice_urn):
      self.recordAction("shutdown", credentials, slice_urn)
      foam.lib.shutdown(slice_urn)
      return True
    return False


def setup (app):
  gapi1 = XMLRPCHandler('gapi1')
  gapi1.connect(app, '/foam/gapi/1')
  gapi1.register_instance(AMAPIv1(app.logger))
  app.logger.info("[GAPIv1] Loaded.")
  return gapi1


