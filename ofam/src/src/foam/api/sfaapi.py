import os
import sys
import random

#legacy optin imports
#from foam.ethzlegacyoptinstuff.legacyoptin.xmlrpcmodels import CallBackServerProxy, FVServerProxy
from foam.ethzlegacyoptinstuff.legacyoptin.optsmodels import Experiment, ExperimentFLowSpace #,\
    #UserOpts, OptsFlowSpace, MatchStruct
from foam.ethzlegacyoptinstuff.legacyoptin.flowspaceutils import dotted_ip_to_int, mac_to_int,\
    int_to_dotted_ip, int_to_mac, parseFVexception

#foam general imports
import logging
import zlib
import base64
import xmlrpclib
from xml.parsers.expat import ExpatError
import jsonrpc
from flaskext.xmlrpc import XMLRPCHandler, Fault
from flask import request
import foam.task
import foam.lib
import foam.api.xmlrpc
import foam.version
from foam.creds import CredVerifier, Certificate
from foam.config import AUTO_SLIVER_PRIORITY, GAPI_REPORTFOAMVERSION
from foam.core.configdb import ConfigDB
from foam.core.log import KeyAdapter

#GENI API imports
from foam.geni.db import GeniDB, UnknownSlice, UnknownNode
import foam.geni.approval
import foam.geni.ofeliaapproval
import foam.geni.lib
import sfa

#FV import
from foam.flowvisor import Connection as FV
from pprint import pprint
import json
import httplib,urllib,base64

THIS_SITE_TAG = ConfigDB.getConfigItemByKey("geni.site-tag").getValue()
from foam.geni.codes import GENI_ERROR_CODE
from foam.ethzlegacyoptinstuff.api_exp_to_rspecv3.expdatatogeniv3rspec import create_ofv3_rspec
from foam.sfa.drivers.OFSfaDriver import OFSfaDriver
from foam.sfa.sfa_config import config as CONFIG
from foam.sfa.methods.permission_manager import PermissionManager
from foam.sfa.lib import get_slice_details_from_slivers, getAdvertisement

def _same(val):
        return "%s" % val

class SfaApi(foam.api.xmlrpc.Dispatcher):
  def __init__ (self, log):
    super(SfaApi, self).__init__("sfaapi", log)
    self._actionLog = KeyAdapter("expedient-sfa", logging.getLogger('sfaapi-actions'))
    #retrieve updated dict as a json file from foam db folder
    filedir = './opt/ofelia/ofam/local/db'
    filename = os.path.join(filedir, 'expedient_slices_info.json')
    if os.path.isfile(filename):
      f = open(filename, 'r')
      self.slice_info_dict = json.load(f)
      f.close()
    else:
      self.slice_info_dict = {}
    #if ConfigDB.getConfigItemByKey("flowvisor.hostname").getValue() is None:
    self.switch_dpid_list = None
    self.link_list = None
    self.callback_http_attr_list = [] #we have multiple expedients communicating with foam!
    self.callback_cred_attr_list = [] #we have multiple expedients communicating with foam!
    self.driver = OFSfaDriver()
    self.pm = PermissionManager()    

  def pub_GetVersion(self,api=None,options={}):
    #FIXME: SFA seems not accept the error GENI structure when exceptions are rised.
    version = {'urn':CONFIG.URN,
               'hostname':CONFIG.HOSTNAME,
               'code_tag':CONFIG.CODE_TAG,
               'hrn':CONFIG.HRN,
               'testbed':CONFIG.TESTBED,
               'geni_api_versions': CONFIG.GENI_API_VERSIONS,
               'interface':CONFIG.INTERFACE,
               'geni_api':int(CONFIG.GENI_API_VERSION),
               'geni_ad_rspec_versions': CONFIG.GENI_AD_RSPEC_VERSIONS,
               'code_url': CONFIG.CODE_URL,
               'geni_request_rspec_versions': CONFIG.GENI_REQUEST_RSPEC_VERSIONS,
               'sfa':int(CONFIG.SFA_VERSION),
               #F4F required params
               'f4f_describe_testbed':CONFIG.DESCRIBE_TESTBED,
               'f4f_testbed_homepage':CONFIG.TESTBED_HOMEPAGE,
               'f4f_testbed_picture':CONFIG.TESTBED_PICTURE,
               'f4f_endorsed_tools':CONFIG.ENDORSED_TOOLS,
               }

    return self.buildPropertyList(GENI_ERROR_CODE.SUCCESS, value=version)

  def pub_ListResources(self,creds=[],options={}):
    self.pm.check_permissions('ListResources',locals())
    slice_xrn = options.get('geni_slice_urn', None)
    propertyList = None
    if slice_xrn:
      xrn = Xrn(slice_xrn,'slice')
      slice_urn = xrn.get_urn()
      slice_leaf = xrn.get_leaf()
      options['slice'] = slice_leaf
    else:
      slice_leaf = None
      slice_urn = None
    try: 
      rspec = self.driver.list_resources(slice_urn,slice_leaf,options)
      if options.has_key('geni_compressed') and options['geni_compressed'] == True:
        rspec = zlib.compress(rspec).encode('base64')
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
    self._log.info(propertyList)
    return propertyList

  def pub_CreateSliver(self, slice_xrn, creds, rspec, users, options):
    """Allocate resources to a slice

    Reserve the resources described in the given RSpec for the given slice, returning a manifest RSpec of what has been reserved.

    """
    try:
      self.pm.check_permissions('CreateSliver',locals())
    except Exception as e: 
      return self.buildPropertyList(GENI_ERROR_CODE.CREDENTIAL_INVALID, output=e)
    self.recordAction("createsliver", creds, slice_xrn)
    user_info = {}
    user_info["urn"] = None
    user_info["email"] = None
    request.environ.pop("CLIENT_RAW_CERT",None)
    sliver = foam.geni.lib.createSliver(slice_xrn, creds, rspec, user_info)
    try:
      approve = foam.geni.approval.analyzeForApproval(sliver)
      style = ConfigDB.getConfigItemByKey("geni.approval.approve-on-creation").getValue()
      if style == foam.geni.approval.NEVER:
        approve = False
      elif style == foam.geni.approval.ALWAYS:
        approve = True
      if approve:
        pid = foam.task.approveSliver(sliver.getURN(), self._auto_priority)

      data = GeniDB.getSliverData(sliver.getURN(), True)
      #foam.task.emailCreateSliver(data)
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.SUCCESS, value=GeniDB.getManifest(sliver.getURN()))

    except foam.geni.lib.RspecParseError as e:
      msg = str(e)
      self._log.info(e)
      return msg
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.BADARGS, output=msg)
    except foam.geni.lib.RspecValidationError as e:
      self._log.info(e)
      msg = str(e)
      return msg
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.BADARGS, output=msg)
    except foam.geni.lib.DuplicateSliver as ds:
      msg = "Attempt to create multiple slivers for slice [%s]" % (ds.slice_urn)
      self._log.info(msg)
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.ERROR, output=msg)
    except foam.geni.lib.UnknownComponentManagerID as ucm:
      msg = "Component Manager ID specified in %s does not match this aggregate." % (ucm.cid)
      self._log.info(msg)
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.ERROR, output=msg)
    except (foam.geni.lib.UnmanagedComponent, UnknownNode) as uc:
      msg = "DPID in component %s is unknown to this aggregate." % (uc.cid)
      self._log.info(msg)
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.ERROR, output=msg)
    except Exception as e:
      msg = "Exception %s" % str(e)
      self._log.info(e)
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.ERROR, output=msg)
    finally:
      return propertyList    

  def pub_DeleteSliver(self, xrn, creds, options={}):
    """Delete a sliver
    Stop all the slice's resources and remove the reservation.
    Returns True or False indicating whether it did this successfully.
    """
    try:
      self.pm.check_permissions('DeleteSliver',locals())
    except Exception as e:
      return self.buildPropertyList(GENI_ERROR_CODE.CREDENTIAL_INVALID, output=e)
    self._log.info("Is HERE:")
    try:
      slivers = GeniDB.getSliverList() 
      self._log.info("Is HERE:")
      sliver = get_slice_details_from_slivers(slivers, xrn)
      self._log.info("Deleteing Sliver")
      self._log.info(sliver["slice_urn"]) 
      data = GeniDB.getSliverData(sliver["sliver_urn"], True)
      foam.geni.lib.deleteSliver(sliver_urn = sliver["sliver_urn"])
      
      #foam.task.emailGAPIDeleteSliver(data)
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.SUCCESS, value=True)

    except UnknownSlice as e:
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.SEARCHFAILED, output=msg)
    except Exception as e:
      msg = "Exception: %s" % str(e)
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.ERROR, output=msg)
    finally:
      return propertyList


  def pub_RenewSliver(self,slice_xrn=None, creds=[], expiration_time=None, options={}):
    try:
        self.pm.check_permissions('Start',locals())
    except Exception as e:
        return self.buildPropertyList(GENI_ERROR_CODE.CREDENTIAL_INVALID, output=e)
    try:
        sliver_urn = foam.lib.renewSliver(slice_xrn, creds, expiration_time)
        data = GeniDB.getSliverData(sliver_xrn, True)
        #foam.task.emailRenewSliver(data)

        propertyList = self.buildPropertyList(GENI_ERROR_CODE.SUCCESS, value=True)
    except foam.lib.BadSliverExpiration as e:
      msg = "Bad expiration request: %s" % (e.msg)
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.ERROR, output=msg)
      e.log(self._log, msg, logging.INFO)
    except Exception as e:
      msg = "Exception: %s" %str(e)
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.ERROR, output=msg)
      self._log.exception(msg)
    finally:
      return propertyList


  def pub_Start(self,xrn, creds):
    try:
        self.pm.check_permissions('Start',locals())
    except Exception as e:
        return self.buildPropertyList(GENI_ERROR_CODE.CREDENTIAL_INVALID, output=e)
    xrn = Xrn(xrn)
    slice_urn = xrn.get_urn()
    slice_leaf = xrn.get_leaf()
    authority = xrn.get_authority_hrn()
    return self.buildPropertyList(GENI_ERROR_CODE.SUCCESS, value=True)

  def pub_Stop(self,xrn, creds):
    try:
        self.pm.check_permissions('Start',locals())
    except Exception as e:
        return self.buildPropertyList(GENI_ERROR_CODE.CREDENTIAL_INVALID, output=e)
    xrn = Xrn(xrn)
    slice_urn = xrn.get_urn()
    slice_leaf = xrn.get_leaf()
    authority = xrn.get_authority_hrn()
    return self.buildPropertyList(GENI_ERROR_CODE.SUCCESS, value=True)

  def pub_reset_slice(self, xrn):
    xrn = Xrn(xrn)
    slice_urn = xrn.get_urn()
    slice_leaf = xrn.get_leaf()
    authority = xrn.get_authority_hrn()
    return self.buildPropertyList(GENI_ERROR_CODE.SUCCESS, value=True)

  def pub_GetTicket(self, api, xrn, creds, rspec, users, options):
    # ticket is dead.
    raise 'Method GetTicket was deprecated.'

  def pub_SliverStatus (self, slice_xrn=None, creds=[], options={}):
    try:
      self.pm.check_permissions('SliverStatus',locals())
    except Exception as e:
      return self.buildPropertyList(GENI_ERROR_CODE.CREDENTIAL_INVALID, output=e)
    try:
      slivers = GeniDB.getSliverList()
      try:
        sliver = get_slice_details_from_slivers(slivers, slice_xrn)
      except:
        raise Exception("Sliver for slice URN (%s) does not exist" % (slice_xrn))
      result= dict()
      result["slice_urn"] = slice_xrn
      result["sliver_urn"] = sliver["sliver_urn"]
      result["status"] = sliver["status"]
      result["created"] = sliver["creation"]
      result["description"] = sliver["desc"]
      result["expires"] = sliver["expiration"]
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.SUCCESS, value=result)
    except UnknownSlice as e:
      msg = "Attempt to get status on unknown sliver for slice %s" % (slice_xrn)
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.SEARCHFAILED, output=msg)
      e.log(self._log, msg, logging.INFO)
    except Exception as e:
      msg = "Exception: %s" % str(e)
      propertyList = self.buildPropertyList(GENI_ERROR_CODE.ERROR, output=msg)
      self._log.exception(msg)
    finally:
      return propertyList

  def pub_Ping(self, message):
     return message

  def buildPropertyList(self, geni_code, value="", output=""):
    #{'output': '', 'geni_api': 2, 'code': {'am_type': 'sfa', 'geni_code': 0}, 'value': rspec}
    result = {}
    result["geni_api"] = 2
    result["code"] = {'geni_code': geni_code , "am_type":"sfa"}
    # Non-zero geni_code implies error: output is required, value is optional
    if geni_code:
      result["output"] = output
      if value:
        result["value"] = value
    # Zero geni_code implies success: value is required, output is optional
    else:
      result["value"] = value
    return result

  def recordAction (self, action, credentials = [], urn = None):
    cred_ids = []
    self._actionLog.info("Sliver: %s  LegExpAPI Action: %s" % (urn, action))
    for cred in credentials:
      self._actionLog.info("Credential: %s" % (cred))
  
def setup (app):
  sfa_api = XMLRPCHandler('sfaapi')
  sfa_api.connect(app, '/sfa/2/')
  sfa_api.register_instance(SfaApi(app.logger))
  app.logger.info("[SfaApi] Loaded.")
  return sfa_api
