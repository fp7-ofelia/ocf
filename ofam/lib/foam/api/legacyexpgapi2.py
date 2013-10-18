# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University
# extended on OFELIA's behalf from Vasileios Kotronis based on gapi1 foam implementation from Nick Bastin
# and of course http://groups.geni.net/geni/wiki/GAPI_AM_API_V2 , where gapi2 is specified
# also used OMNI implementation (gcf-2.1) as reference

#imports same as gapi1
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
import foam.geni.ofeliaapproval
from foam.creds import CredVerifier, Certificate
from foam.config import AUTO_SLIVER_PRIORITY, GAPI_REPORTFOAMVERSION
from foam.core.configdb import ConfigDB
from foam.core.log import KeyAdapter
from foam.geni.db import GeniDB, UnknownSlice, UnknownNode

import foam.geni.lib

import sfa

#further imports that may be needed (see OMNI)
import datetime
import dateutil.parser
import os
import uuid
import xml.dom.minidom as minidom

from foam.api.jsonrpc import Dispatcher, route


#Vasileios: additional class to handle geni am return codes as in 
#https://openflow.stanford.edu/display/FOAM/GENI+-+AM+return+code+proposal
#see ListResources exceptions to check how I use it (code, desc, etc.)
#but: need to retun proper answers with proper error codes
#according to the geni format (working on that: maybe Nick has some advice for that)
class AdditionalException(Exception):
	pass
	

class AMLegExpGeniAPIv2(foam.api.xmlrpc.Dispatcher):
	def __init__ (self, log):
		super(AMLegExpGeniAPIv2, self).__init__("LegExpGAPIv2", log)
		self._actionLog = KeyAdapter("legv2", logging.getLogger('gapi-actions'))
	
	def recordAction (self, action, credentials = [], urn = None):
		cred_ids = []
		self._actionLog.info("Sliver: %s  LegExpGAPIv2 Action: %s" % (urn, action))
		for cred in credentials:
			self._actionLog.info("Credential: %s" % (cred))
		
	def pub_GetVersion  (self):
		self.recordAction("getversion")
		d ={"geni_api" : 2,
				"code" : {
						'geni_code' : 0
				},
				"value" : {
						"geni_api_versions" : {
								'1' : 'https://localhost:3626/foam/gapi/1',
								'2' : 'https://localhost:3626/foam/gapi/2'
						},
						"geni_request_rspec_versions" : [
								{ 'type': 'geni',
									'version': '3',
									'schema': 'http://www.geni.net/resources/rspec/3/request.xsd',
									'namespace': 'http://www.geni.net/resources/rspec/3',
									'extensions': [ 'http://www.geni.net/resources/rspec/ext/openflow/3',
																	'http://www.geni.net/resources/rspec/ext/openflow/4',
																	'http://www.geni.net/resources/rspec/ext/flowvisor/1', ]}
						],
						"geni_ad_rspec_versions" : [
								{ 'type': 'geni',
									'version': '3',
									'schema': 'http://www.geni.net/resources/rspec/3/ad.xsd',
									'namespace': 'http://www.geni.net/resources/rspec/3',
									'extensions': [ 'http://www.geni.net/resources/rspec/ext/openflow/3' ]}
						],
				},
				"output" : ""
				}
		#legacy from foam, not sure if I can accumulate it correctly in return d, depends
		#on how the other end (in our case Expedient) will interpret it
		#d["site_info"] = self.generateSiteInfo()
		
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
		#try verifying creds and privs and produce rspec as in gapi1
		try:
			CredVerifier.checkValid(credentials, [])
			available = options.get("geni_available", False) #isn't currently handled
			compressed = options.get("geni_compressed", False) #handled
			urn = options.get("geni_slice_urn", None) #handled
			rspec_version = options.get("geni_rspec_version", None) #working on it
			
			#handle rspec_version properly, need to test if my code is right
			if rspec_version is None:
				# This is a required option, so error out with bad arguments.
				#self._log.error("No geni_rspec_version supplied to ListResources.")
				addEx = AdditionalException("BADARGS")
				addEx.code = 1 
				addEx.desc = "Bad Arguments: option geni_rspec_version was not supplied."
				raise addEx
			
			type = rspec_version.get("type", None)
			if type is None:
				#self._log.error("ListResources: geni_rspec_version does not contain a type field.")
				addEx = AdditionalException("BADARGS")
				addEx.code = 1 
				addEx.desc = "Bad Arguments: option geni_rspec_version does not have a type field."
				raise addEx
        
			ver = rspec_version.get("version", None)
			if ver is None:
				#self._log.error("ListResources: geni_rspec_version does not contain a version field.")
				addEx = AdditionalException("BADARGS")
				addEx.code = 1 
				addEx.desc = "Bad Arguments: option geni_rspec_version does not have a version field."
				raise addEx
			
			#check if rspec version requested by client is compatible
			#with the one supported by our foam AM
			if type != 'geni':
				#self._log.error("ListResources: Unknown RSpec type %s requested", type)
				addEx = AdditionalException("BADVERSION")
				addEx.code = 4
				addEx.desc = "Bad Version: requested RSpec type %s is not a valid option." % type
				raise addEx    
				
			if ver != '3':
				#self._log.error('ListResources: Unknown RSpec version %s requested', rspec_version)
				addEx = AdditionalException("BADVERSION")
				addEx.code = 4
				addEx.desc = "Bad Version: requested RSpec version %s is not a valid option." % ver
				raise addEx
						
			self._log.info("ListResources requested RSpec of type %s and version %s" % (type, ver))

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
			return self.successResult(rspec)
									
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
		except AdditionalException, e:
			self._log.error(str(e.code) + ":" + e.desc)
			e._foam_logged = True
			return self.errorResult(e.code, "")
			#raise Exception
		except Exception, e:
			self._log.exception("Exception")
			raise e
	
	def pub_CreateSliver(self, slice_urn, credentials, rspec, users, options):	
		#user_info = {}
		user_info = users
		try:
			#if CredVerifier.checkValid(credentials, "createsliver"):
			if True:
				self.recordAction("createsliver", credentials, slice_urn)
				try:
					#cert = Certificate(request.environ['CLIENT_RAW_CERT'])
					#user_info["urn"] = cert.getURN()
					#user_info["email"] = cert.getEmailAddress()
					self._log.debug("Parsed user cert with URN (%(urn)s) and email (%(email)s)" % user_info)
				except Exception, e:
					self._log.exception("UNFILTERED EXCEPTION")
					user_info["urn"] = None
					user_info["email"] = None
				sliver = foam.geni.lib.createSliver(slice_urn, credentials, rspec, user_info)
				approve = foam.geni.ofeliaapproval.of_analyzeForApproval(sliver)
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
				return self.successResult(GeniDB.getManifest(sliver.getURN()))
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
		except AdditionalException, e:
			self._log.error(str(e.code) + ":" + e.desc)
			e._foam_logged = True
			return self.errorResult(e.code, "")
			#raise Exception
		except Exception, e:
			self._log.exception("Exception")
			raise e
		
	def pub_DeleteSliver(self, slice_urn, credentials, options):
		try:
			#if CredVerifier.checkValid(credentials, "deletesliver", slice_urn):
			if True:
				self.recordAction("deletesliver", credentials, slice_urn)
				if GeniDB.getSliverURN(slice_urn) is None:
					raise Fault("DeleteSliver", "Sliver for slice URN (%s) does not exist" % (slice_urn))
					return self.errorResult(12, "") #not sure if this is needed
				sliver_urn = GeniDB.getSliverURN(slice_urn)
				data = GeniDB.getSliverData(sliver_urn, True)
				foam.geni.lib.deleteSliver(sliver_urn = sliver_urn)
				foam.task.emailGAPIDeleteSliver(data)
				return self.successResult(True)
			return self.successResult(False)
		
		except UnknownSlice, x:
			self._log.info("Attempt to delete unknown sliver for slice URN %s" % (slice_urn))
			x._foam_logged = True
			raise x
		except Exception, e:
			self._log.exception("Exception")
			raise e
	
	def pub_SliverStatus(self, slice_urn, credentials, options):
		try:
			if CredVerifier.checkValid(credentials, "sliverstatus", slice_urn):
				self.recordAction("sliverstatus", credentials, slice_urn)
				result = {}
				sliver_urn = GeniDB.getSliverURN(slice_urn)
				if not sliver_urn:
					raise Fault("SliverStatus", "Sliver for slice URN (%s) does not exist" % (slice_urn))
					return self.errorResult(12, "") #not sure if this is needed
				sdata = GeniDB.getSliverData(sliver_urn, True)
				status = foam.geni.lib.getSliverStatus(sliver_urn)
				result["geni_urn"] = sliver_urn
				result["geni_status"] = status
				result["geni_resources"] = [{"geni_urn" : sliver_urn, "geni_status": status, "geni_error" : ""}]
				#legacy from foam, not sure if I can accumulate it correctly in return result, depends
				#on how the other end (in our case Expedient) will interpret it
				#result["foam_status"] = sdata["status"]
				#result["foam_expires"] = sdata["expiration"]
				#result["foam_pend_reason"] = sdata["pend_reason"]
				return self.successResult(result)
			return self.successResult(False) #maybe we should do something more formal about this "False"
		
		except UnknownSlice, x:
			self._log.info("Attempt to get status on unknown sliver for slice %s" % (slice_urn))
			x._foam_logged = True
			raise x
		except Exception, e:
			self._log.exception("Exception")
			raise e
	
	def pub_RenewSliver(self, slice_urn, credentials, expiration_time, options):
		try:
			if CredVerifier.checkValid(credentials, "renewsliver", slice_urn):
				self.recordAction("renewsliver", credentials, slice_urn)
				creds = CredVerifier.fromStrings(credentials, "renewsliver", slice_urn)
				#corrected a small ommision
				if not GeniDB.getSliverURN(slice_urn):
					raise Fault("renewSliver", "Sliver for slice URN (%s) does not exist" % (slice_urn))
					return self.errorResult(12, "") #not sure if this is needed
				sliver_urn = foam.lib.renewSliver(slice_urn, creds, exptime)
				data = GeniDB.getSliverData(sliver_urn, True)
				foam.task.emailRenewSliver(data)
				return self.successResult(True)
			return self.successResult(True)
		
		except foam.lib.BadSliverExpiration, e:
			self._log.info("Bad expiration request: %s" % (e.msg))
			e._foam_logged = True
			raise e
		except Exception, e:
			self._log.exception("Exception")
			raise e
	
	def pub_Shutdown(self, slice_urn, credentials, options):
		try:
			if CredVerifier.checkValid(credentials, "shutdown", slice_urn):
				self.recordAction("shutdown", credentials, slice_urn)
				if GeniDB.getSliverURN(slice_urn) is None:
					raise Fault("ShutdownSliver", "Sliver for slice URN (%s) does not exist" % (slice_urn))
					return self.errorResult(12, "") #not sure if this is needed
				sliver_urn = GeniDB.getSliverURN(slice_urn)
				data = GeniDB.getSliverData(sliver_urn, True)
				foam.geni.lib.deleteSliver(sliver_urn = sliver_urn)
				#foam.task.emailGAPIDeleteSliver(data)
				#foam.lib.shutdown(slice_urn) #but this medthod is not within foam.lib!!! 
				#Where is shutdown located then??? Help needed :)
				#probably need to implement it from scratch or just use deletesliver
				return self.successResult(True)
			return self.successResult(True)
		except Exception, e:
			self._log.exception("Exception")
			raise e
		
	#additional methods from OMNI ref AM impl., to return results with proper codes and values
	#we will see how we will use them
	def successResult(self, value):
		code_dict = dict(geni_code=0)
		return dict(code=code_dict,
								value=value,
								output="")
										
	def errorResult(self, code, output):
		code_dict = dict(geni_code=code)
		return dict(code=code_dict,
								value="",
								output=output)

	#Expedient shoudld be able to get the current switch topology
	#but only using superuser creds (a normal user cannot call this method)
	def adm_CallCurrentTopology(self, credentials): #to be implemented
		pass
	

#setup same as gapi1 (change version nums of course)
def setup (app):
  legexpgapi2 = XMLRPCHandler('legexpgapi2')
  legexpgapi2.connect(app, '/foam/legexpgapi/2')
  #legexpgapi2 = AMLegExpGeniAPIv2(app)
  legexpgapi2.register_instance(AMLegExpGeniAPIv2(app.logger))
  app.logger.info("[LegExpGAPIv2] Loaded.")
  return legexpgapi2
