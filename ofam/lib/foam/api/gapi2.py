# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# substituted code with 0.11-DEV gapi2 code by Nick (to be tested)

import logging
import zlib
import base64
import xmlrpclib
from xml.parsers.expat import ExpatError

from flaskext.xmlrpc import XMLRPCHandler
from flask import request

import foam.task
import foam.lib
import foam.api.xmlrpc
import foam.version
import foam.geni.approval
import foam.geni.ofeliaapproval
from foam.creds import CredVerifier, Certificate
from foam.config import AUTO_SLIVER_PRIORITY, GAPI_REPORTFOAMVERSION
from foam.core.configdb import ConfigDB
from foam.core.log import KeyAdapter
from foam.geni.db import GeniDB, UnknownSlice, UnknownNode

import foam.geni.lib
from foam.geni.codes import GENI_ERROR_CODE

import sfa

class AMAPIv2(foam.api.xmlrpc.Dispatcher):
  """Implementation of GENI AM API v2"""
  def __init__ (self, log):
    super(AMAPIv2, self).__init__("GAPIv2", log)
    self._actionLog = KeyAdapter("v2", logging.getLogger('gapi-actions'))
    #self._auto_priority = ConfigDB.getConfigItemByKey("geni.auto-sliver-priority").getValue()
    self._auto_priority = AUTO_SLIVER_PRIORITY

  def recordAction (self, action, credentials = [], urn = None):
    cred_ids = []

    self._actionLog.info("Sliver: %s  Action: %s" % (urn, action))

    for cred in credentials:
      self._actionLog.info("Credential: %s" % (cred))

  def buildPropertyList(self, geni_code, value=None, output=None):
    """Return XML-RPC struct (aka property list)"""
    result = {}
    result["code"] = {'geni_code': geni_code}
    # Non-zero geni_code implies error: output is required, value is optional
    if geni_code:
      result["output"] = output
      if value:
        result["value"] = value
    # Zero geni_code implies success: value is required, output is optional
    else:
      result["value"] = value
    return result

  def pub_GetVersion (self, options=None):
    """Return the version of the GENI AM API and RSpecs supported

    Get static version and configuration information about this aggregate.

    """
    self.recordAction("getversion")
    url = "https://%s:%s" % (request.environ['SERVER_ADDR'], request.environ['SERVER_PORT'])
    d = { 'geni_api': '2',
          'geni_request_rspec_versions': [
            { 'extensions': ['http://www.geni.net/resources/rspec/ext/openflow/3'],
              'namespace' : 'http://www.geni.net/resources/rspec/3',
              'schema': 'http://www.geni.net/resources/rspec/3/request.xsd',
              'type': 'GENI',
              'version': '3'
            }
          ],            
          'geni_ad_rspec_versions': [
            { 'extensions': [ 'http://www.geni.net/resources/rspec/ext/openflow/3' ],
              'namespace': 'http://www.geni.net/resources/rspec/3',
              'schema': 'http://www.geni.net/resources/rspec/3/ad.xsd',
              'type': 'GENI',
              'version': '3'
            }
          ],
          'geni_api_versions': {
            '1': url + '/foam/gapi/1',
            '2': url + '/foam/gapi/2'
          }
        }
    #if ConfigDB.getConfigItemByKey("geni.report-foam-version").getValue():
    #  d["foam_version"] = foam.version.VERSION
    #if ConfigDB.getConfigItemByKey("geni.report-site-info").getValue():
    #  d["site_info"] = self.generateSiteInfo()
    if GAPI_REPORTFOAMVERSION:
      d["foam_version"] = foam.version.VERSION
    d["site_info"] = self.generateSiteInfo()

    result = self.buildPropertyList(GENI_ERROR_CODE.SUCCESS, value=d)

    # geni_api is duplicated under value to allow v1 clients to determine the AM API version
    result["geni_api"] = 2

    return result

  def generateSiteInfo (self):
    """Generate site's admin, location and description info"""
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
    """Return information about available resources or resources allocated to a slice

    List the resources at this aggregate in an RSpec: may be all resources,
    only those available for reservation, or only those already reserved for the given slice.

    """
    try:
      CredVerifier.checkValid(credentials, [])

      # Parse options
      compressed = options.get("geni_compressed", False)
      urn = options.get("geni_slice_urn", None)
      spec_version = options.get("geni_rspec_version")
      supported_spec = {'version': '3', 'type': 'GENI'}
      if spec_version:
        if spec_version != supported_spec:
          msg = "RSpec type/version not supported"
          propertyList = self.buildPropertyList(GENI_ERROR_CODE.BADVERSION, output=msg)
          return propertyList
      else:
        msg = "Required option geni_rspec_version missing"
        propertyList = self.buildPropertyList(GENI_ERROR_CODE.BADARGS, output=msg)
        return propertyList

      if urn:
        CredVerifier.checkValid(credentials, "getsliceresources", urn)
        self.recordAction("listresources", credentials, urn)
        sliver_urn = GeniDB.getSliverURN(urn)
        if sliver_urn is None:
          raise Exception("Sliver for slice URN (%s) does not exist" % (urn))
        else:
          rspec = GeniDB.getManifest(sliver_urn)
      else:
        self.recordAction("listresources", credentials)
        rspec = foam.geni.lib.getAdvertisement()
      if compressed:
        zrspec = zlib.compress(rspec)
        rspec = base64.b64encode(zrspec)

      propertyList = self.buildPropertyList(GENI_ERROR_CODE.SUCCESS, value=rspec)

    except ExpatError:
      msg = "Error parsing credential strings"
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.BADARGS, output=msg)
      self._log.error(msg)
    except UnknownSlice as x:
      # Raised by GeniDB.getSliverURN()
      msg = "Attempt to list resources on sliver for unknown slice %s" % (urn)
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.ERROR, output=msg)
      x.log(self._log, msg, logging.INFO)
    except xmlrpclib.Fault as x:
      # Something thrown via GCF, we'll presume it was something related to credentials
      msg = "GCF credential check failure: <%s>" % (x)
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.ERROR, output=msg)
      self._log.info(msg)
      self._log.debug(x, exc_info=True)
    except AttributeError as x:
      # New GCF problem with user creds that have no gid_caller, probably
      msg = "GCF credential check failure: <%s>" % (x)
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.ERROR, output=msg)
      self._log.info(msg)
      self._log.debug(x, exc_info=True)
    except Exception as e:
      msg = "Exception: %s" % str(e)
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.ERROR, output=msg)
      self._log.exception(msg)
    finally:
      return propertyList

  def pub_CreateSliver (self, slice_urn, credentials, rspec, users, options):
    """Allocate resources to a slice

    Reserve the resources described in the given RSpec for the given slice, returning a manifest RSpec of what has been reserved.

    """
    
    user_info = {}
    try:
      if CredVerifier.checkValid(credentials, "createsliver"):
        self.recordAction("createsliver", credentials, slice_urn)
        try:
          cert = Certificate(request.environ['CLIENT_RAW_CERT'])
          user_info["urn"] = cert.getURN()
          user_info["email"] = cert.getEmailAddress()
          self._log.debug("Parsed user cert with URN (%(urn)s) and email (%(email)s)" % user_info)
        except Exception as e:
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
          pid = foam.task.approveSliver(sliver.getURN(), self._auto_priority)
          self._log.debug("task.py launched for approve-sliver (PID: %d)" % pid)

        data = GeniDB.getSliverData(sliver.getURN(), True)
        foam.task.emailCreateSliver(data)

        propertyList = self.buildPropertyList(GENI_ERROR_CODE.SUCCESS, value=GeniDB.getManifest(sliver.getURN()))

    except foam.geni.lib.RspecParseError as e:
      msg = str(e)
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.BADARGS, output=msg)
      e.log(self._log, msg, logging.INFO)
    except foam.geni.lib.RspecValidationError as e:
      msg = str(e)
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.BADARGS, output=msg)
      e.log(self._log, msg, logging.INFO)
    except foam.geni.lib.DuplicateSliver as ds:
      msg = "Attempt to create multiple slivers for slice [%s]" % (ds.slice_urn)
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.ERROR, output=msg)
      ds.log(self._log, msg, logging.INFO)
    except foam.geni.lib.UnknownComponentManagerID as ucm:
      msg = "Component Manager ID specified in %s does not match this aggregate." % (ucm.cid)
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.ERROR, output=msg)
      ucm.log(self._log, msg, logging.INFO)
    except (foam.geni.lib.UnmanagedComponent, UnknownNode) as uc:
      msg = "DPID in component %s is unknown to this aggregate." % (uc.cid)
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.ERROR, output=msg)
      uc.log(self._log, msg, logging.INFO)
    except Exception:
      msg = "Exception"
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.ERROR, output=msg)
      self._log.exception(msg)
    finally:
      return propertyList

  def pub_DeleteSliver (self, slice_urn, credentials, options):
    """Delete a sliver

    Stop all the slice's resources and remove the reservation.
    Returns True or False indicating whether it did this successfully.

    """
    try:
      if CredVerifier.checkValid(credentials, "deletesliver", slice_urn):
        self.recordAction("deletesliver", credentials, slice_urn)
        if GeniDB.getSliverURN(slice_urn) is None:
          raise UnkownSlice(slice_urn)

        sliver_urn = GeniDB.getSliverURN(slice_urn)
        data = GeniDB.getSliverData(sliver_urn, True)

        foam.geni.lib.deleteSliver(sliver_urn = sliver_urn)

        foam.task.emailGAPIDeleteSliver(data)

        propertyList = self.buildPropertyList(GENI_ERROR_CODE.SUCCESS, value=True)

    except UnknownSlice as e:
      msg = "Attempt to delete unknown sliver for slice URN %s" % (slice_urn)
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.SEARCHFAILED, output=msg)
      e.log(self._log, msg, logging.INFO)
    except Exception as e:
      msg = "Exception: %s" % str(e)
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.ERROR, output=msg)
      self._log.exception("Exception")
    finally:
      return propertyList

  def pub_SliverStatus (self, slice_urn, credentials, options):
    """Returns the status of the reservation for this slice at this aggregate"""
    try:
      if CredVerifier.checkValid(credentials, "sliverstatus", slice_urn):
        self.recordAction("sliverstatus", credentials, slice_urn)
        result = {}
        sliver_urn = GeniDB.getSliverURN(slice_urn)
        if not sliver_urn:
          raise Exception("Sliver for slice URN (%s) does not exist" % (slice_urn))
        sdata = GeniDB.getSliverData(sliver_urn, True)
        status = foam.geni.lib.getSliverStatus(sliver_urn)
        result["geni_urn"] = sliver_urn
        result["geni_status"] = status
        result["geni_resources"] = [{"geni_urn" : sliver_urn, "geni_status": status, "geni_error" : ""}]
        result["foam_status"] = sdata["status"]
        result["foam_expires"] = sdata["expiration"]
        result["foam_pend_reason"] = sdata["pend_reason"]
        propertyList = self.buildPropertyList(GENI_ERROR_CODE.SUCCESS, value=result)
    except UnknownSlice as e:
      msg = "Attempt to get status on unknown sliver for slice %s" % (slice_urn)
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.SEARCHFAILED, output=msg)
      e.log(self._log, msg, logging.INFO)
    except Exception as e:
      msg = "Exception: %s" % str(e)
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.ERROR, output=msg)
      self._log.exception(msg)
    finally:
      return propertyList

  def pub_RenewSliver (self, slice_urn, credentials, exptime, options):
    """Renew the reservation for resources in this slice"""
    try:
      if CredVerifier.checkValid(credentials, "renewsliver", slice_urn):
        self.recordAction("renewsliver", credentials, slice_urn)
        creds = CredVerifier.fromStrings(credentials, "renewsliver", slice_urn)
        sliver_urn = foam.lib.renewSliver(slice_urn, creds, exptime)

        data = GeniDB.getSliverData(sliver_urn, True)
        foam.task.emailRenewSliver(data)

        propertyList = self.buildPropertyList(GENI_ERROR_CODE.SUCCESS, value=True)
    except foam.lib.BadSliverExpiration as e:
      msg = "Bad expiration request: %s" % (e.msg)
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.ERROR, output=msg)
      e.log(self._log, msg, logging.INFO)
    except Exception:
      msg = "Exception"
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.ERROR, output=msg)
      self._log.exception("Exception")
    finally:
      return propertyList

  def pub_Shutdown (self, slice_urn, credentials, options):
    """Perform an emergency shutdown of the resources in a slice at this aggregate"""
    if CredVerifier.checkValid(credentials, "shutdown", slice_urn):
      self.recordAction("shutdown", credentials, slice_urn)
      #foam.lib.shutdown(slice_urn)
      sliver_urn = GeniDB.getSliverURN(slice_urn)
      data = GeniDB.getSliverData(sliver_urn, True)
      foam.geni.lib.deleteSliver(sliver_urn = sliver_urn)
      return self.buildPropertyList(GENI_ERROR_CODE.SUCCESS, value=True)
    return self.buildPropertyList(GENI_ERROR_CODE.SUCCESS, value=False)

def setup (app):
  gapi2 = XMLRPCHandler('gapi2')
  gapi2.connect(app, '/foam/gapi/2')
  gapi2.register_instance(AMAPIv2(app.logger))
  app.logger.info("[GAPIv2] Loaded.")
  return gapi2

