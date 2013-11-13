# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University

import traceback
import hashlib

from flask import request

from foam.flowvisor import Connection as FV
from foam.core.json import jsonify, jsonValidate, JSONValidationError
from foam.api.jsonrpc import Dispatcher, route
from foam import types
import foam.task
import foam.lib
import foam.geni.lib
from foam.geni.db import GeniDB
from foam.core.configdb import ConfigDB
import os, sys
import json
import foam.ofeliasettings.localsettings as locsettings

from foam.ethzlegacyoptinstuff.legacyoptin.optsmodels import Experiment, ExperimentFLowSpace
from foam.ethzlegacyoptinstuff.legacyoptin.flowspaceutils import dotted_ip_to_int, mac_to_int,\
    int_to_dotted_ip, int_to_mac, parseFVexception
from foam.ethzlegacyoptinstuff.api_exp_to_rspecv3.expdatatogeniv3rspec import *

import time, random

def _same(val):
	return "%s" % val 

class om_ch_translate(object): 
  attr_funcs = {
    # attr_name: (func to turn to str, width)
    "dl_src": (int_to_mac, mac_to_int, 48, "mac_src","dl_src"),
    "dl_dst": (int_to_mac, mac_to_int, 48, "mac_dst","dl_dst"),
    "dl_type": (_same, int, 16, "eth_type","dl_type"),
    "vlan_id": (_same, int, 12, "vlan_id","dl_vlan"),
    "nw_src": (int_to_dotted_ip, dotted_ip_to_int, 32, "ip_src","nw_src"),
    "nw_dst": (int_to_dotted_ip, dotted_ip_to_int, 32, "ip_dst","nw_dst"),
    "nw_proto": (_same, int, 8, "ip_proto","nw_proto"),
    "tp_src": (_same, int, 16, "tp_src","tp_src"),
    "tp_dst": (_same, int, 16, "tp_dst","tp_dst"),
    "port_num": (_same, int, 16, "port_number","in_port"),
    }


class AdminAPIv1(Dispatcher):
  def __init__ (self, app):
    super(AdminAPIv1, self).__init__("Admin v1", app.logger, app)
    self.vlan_automation_on = False
    self._log.info("Loaded")

  def validate (self, rjson, types):
    return jsonValidate(rjson, types, self._log)

  @route('/core/admin/get-fv-slice-name', methods=["POST"])
  def getFVSliceName (self):
    if not request.json:
      return
    try:
      self.validate(request.json, [("slice_urn", (unicode,str))])
      name = GeniDB.getFlowvisorSliceName(request.json["slice_urn"])
      return jsonify({"name" : name})
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/admin/list-slivers', methods=["POST", "GET"])
  def listSlivers (self):
    try:
      deleted = False
      status = 0

      if request.method == "POST":
        if not request.json:
          return ""
        if request.json.has_key("deleted"):
          deleted = request.json["deleted"]
        if request.json.has_key("status"):
          st = request.json["status"].lower()
          if st == "approved":
            status = True
          elif st == "rejected":
            status = False
          elif st == "pending":
            status = None

      slivers = GeniDB.getSliverList(deleted, status)
      return jsonify({"slivers" : slivers})
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg = traceback.format_exc())

  @route('/core/admin/approve-sliver', methods=["POST"])
  def approveSliver (self):
    if not request.json:
      return
    return foam.geni.lib.approveSliver(request, self._log)

  @route('/core/admin/reject-sliver', methods=["POST"])
  def rejectSliver (self):
    if not request.json:
      return
    try:
      self.validate(request.json, [("sliver_urn", (unicode,str))])
      slice_name = GeniDB.getFlowvisorSliceName(sliver_urn=request.json["sliver_urn"])
      sobj = GeniDB.getSliverObj(request.json["sliver_urn"])

      data = GeniDB.getSliverData(sobj.getURN(), True)

      GeniDB.setSliverStatus(request.json["sliver_urn"], False)
      if FV.sliceExists(slice_name):
        FV.deleteSlice(slice_name)

      foam.task.emailRejectSliver(data)

      return jsonify(None)
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/admin/disable-sliver', methods=["POST"])
  def disableSliver (self):
    if not request.json:
      return
    try:
      self.validate(request.json, [("sliver_urn", (unicode,str))])
      slice_name = GeniDB.getFlowvisorSliceName(sliver_urn=request.json["sliver_urn"])
      sobj = GeniDB.getSliverObj(request.json["sliver_urn"])

      data = GeniDB.getSliverData(sobj.getURN(), True)

      GeniDB.setSliverStatus(request.json["sliver_urn"], None)
      GeniDB.commit()

      if FV.sliceExists(slice_name):
        FV.deleteSlice(slice_name)

      foam.task.emailDisableSliver(data)

      return jsonify(None)
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/admin/delete-sliver', methods=["POST"])
  def deleteSliver (self):
    if not request.json:
      return
    try:
      self.validate(request.json, [("sliver_urn", (unicode,str))])

      data = GeniDB.getSliverData(request.json["sliver_urn"], True)

      foam.geni.lib.deleteSliver(sliver_urn=request.json["sliver_urn"])

      foam.task.emailJSONDeleteSliver(data)

      return jsonify(None)
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())
      
  @route('/core/admin/show-sliver', methods=["POST"])
  def showSliver (self):
#    from foam.core.tracer import Tracer
#    Tracer.enable()

    if not request.json:
      return

    try:
      return_obj = {}

      self.validate(request.json, [("sliver_urn", (unicode,str))])

      sobj = GeniDB.getSliverObj(request.json["sliver_urn"])
      return_obj["sliver"] = sobj

      if request.json.has_key("flowspace") and request.json["flowspace"]:
        return_obj["flowspace"] = sobj.generateFlowEntries()

      if request.json.has_key("flowspec") and request.json["flowspec"]:
        return_obj["flowspec"] = sobj.json_flowspec()

      if request.json.has_key("rspec") and request.json["rspec"]:
        return_obj["rspec"] = GeniDB.getRspec(request.json["sliver_urn"])

#      path = Tracer.disable()
#      self._log.debug("Tracer path: %s" % (path))

      return jsonify(return_obj)
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/admin/get-config', methods=["POST"])
  def getConfig (self):
    if not request.json:
      return

    try:
      objs = self.validate(request.json, [("key", (unicode,str))])
      u = ConfigDB.getUser(request.environ["USER"])
      # Don't look here - stupidity to get around the fact that we don't
      # have output processors
      if objs["key"] == "geni.max-lease":
        val = ConfigDB.getConfigItemByKey("geni.max-lease").getValue(u)
        return jsonify({"value" : str(val)})
      else:
        return jsonify({"value" : ConfigDB.getConfigItemByKey(request.json["key"]).getValue(u)})
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except TypeError, e:
      return jsonify(None, 3, msg = "Unknown key (%s)" % (objs["key"]))
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg = traceback.format_exc())

  @route('/core/admin/set-config', methods=["POST"])
  def setConfig (self):
    if not request.json:
      return
    try:
      objs = self.validate(request.json, [("key", (unicode,str)), ("value", (dict, int, unicode, str))])
      u = ConfigDB.getUser(request.environ["USER"])
      key = request.json["key"]
      ConfigDB.getConfigItemByKey(request.json["key"]).write(request.json["value"], u)
      return jsonify({"status" : "success"})
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())


  @route('/core/admin/get-sliver-flowspace', methods=["POST"])
  def getSliverFlowspace (self):
    if not request.json:
      return
    try:
      self.validate(request.json, [("sliver_urn", (unicode,str))])
      sobj = GeniDB.getSliverObj(request.json["sliver_urn"])
      return jsonify({"flowspace" : sobj.generateFlowEntries()})
    except JSONValidationError, e:
      return jsonify(e.__json__())
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/admin/get-version', methods=["GET"])
  def jsonGetVersion (self):
    try:
      import foam.version
      return jsonify({"version" : foam.version.VERSION})
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/admin/set-location', methods=["POST"])
  def setLocation (self):
    if not request.json:
      return
    try:
      self.validate(request.json, [("lat", float), ("long", float), ("dpid", (unicode,str)), ("country", (unicode,str))])
      GeniDB.setLocation(request.json["dpid"], request.json["country"], request.json["lat"], request.json["long"])
      return jsonify({"status" : "success"})
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/admin/add-datapath', methods=["POST"])
  def addDatapath (self):
    if not request.json:
      return

    try:
      self.validate(request.json, [("dpid", (unicode,str))])
      GeniDB.addDatapath(request.json["dpid"])
      return jsonify({"status" : "success"})
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/admin/remove-datapath', methods=["POST"])
  def removeDatapath (self):
    if not request.json:
      return

    try:
      self.validate(request.json, [("dpid", (unicode,str))])
      GeniDB.removeDatapath(request.json["dpid"])
      return jsonify({"status" : "success"})
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/admin/set-trigger', methods=["POST"])
  def setTrigger (self):
    if not request.json:
      return
    try:
      obj = self.validate(request.json, [("type", types.TriggerType), ("start", (str,unicode)),
                              ("end", (str,unicode)), ("event", types.EventType),
                              ("action", None)])
      GeniDB.addTrigger(obj["type"], obj["start"], obj["end"], obj["event"], obj["action"])
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/admin/set-sliver-expiration', methods=["POST"])
  def adminSetSliverExpiration (self):
    if not request.json:
      return
    try:
      objs = self.validate(request.json, [("datetime", types.DateTime), ("urn", types.SliverURN)])
      GeniDB.updateSliverExpiration(objs["urn"], objs["datetime"])
      return jsonify({"status" : "success"})
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/admin/rebuild-flowvisor-cache', methods=["GET"])
  def adminRebuildFlowvisorCache (self):
    try:
      FV.rebuildCache()
      return jsonify(None)
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/admin/begin-import', methods=["GET"])
  def adminBeginImport (self):
    try:
      ConfigDB.importing = True
      return jsonify(None)
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/admin/finish-import', methods=["GET"])
  def adminFinishImport (self):
    try:
      ConfigDB.importing = False
      return jsonify(None)
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/admin/import-sliver', methods=["POST"])
  def adminImportSliver (self):
    if not request.json:
      return
    try:
      objs = self.validate(request.json, [("slice_urn", (str, unicode)), 
                                          ("sliver_urn", (str, unicode)),
                                          ("fvslicename", (str, unicode)),
                                          ("req_rspec", (str, unicode)),
                                          ("manifest_rspec", (str, unicode)),
                                          ("exp", (types.DateTime)),
                                          ("priority", (int)),
                                          ("status", (bool)),
                                          ("deleted", (bool))])
      self._log.info("Importing sliver %s" % (objs["sliver_urn"]))
      obj = foam.geni.lib.importSliver(objs)
      return jsonify(None)
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  #VLAN handling code-base start
	
  #Vasileios's code for listing all vlans (before Leo's vlancontroller)
  @route('/core/admin/list-vlans', methods=["POST", "GET"])
  def adminListVLANs (self): #use_json = True
    #if not request.json:
    #  return
    try:			
      global_vlan_list = {}
      for i in range(4095):
        global_vlan_list[i] = "free"

      slivers = GeniDB.getSliverList(False, True, True)
      for sliv in slivers:
        fspecs = sliv.getFlowspecs()
        for fs in fspecs:
          for vlanid in fs.getVLANs():
            global_vlan_list[vlanid] = "allocated"
		
      free_vlan_list = []
      for i in global_vlan_list.iterkeys():
        if global_vlan_list[i] == "free":
          free_vlan_list.append(i)	
      free_vlan_list.sort()
			
      allocated_vlan_list = []
      for i in global_vlan_list.iterkeys():
        if global_vlan_list[i] == "allocated":
          allocated_vlan_list.append(i)	
      allocated_vlan_list.sort()

      for vlan_id in locsettings.UNALLOWED_VLANS:
        free_vlan_list.remove(vlan_id)
		
      #if (use_json == True):
      return jsonify({"free-vlans" : free_vlan_list, "allocated-vlans" : allocated_vlan_list})
      #else:
      #  return {"free-vlans" : free_vlan_list, "allocated-vlans" : allocated_vlan_list}
		
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg = traceback.format_exc())

  #see optin optin_manager/python/openflow/optin_manager/vlans/vlanController.py for the source
  #of the following methods

  #Vasileios: adapt vlanController.get_allocated_vlans method
  @route('/core/admin/list-allocated-vlans', methods=["POST", "GET"])
  def adminListAllocatedVlans(self, use_json = True):
    #if not request.json:
    #  return
    try:
      used_vlans = []
      slivers = GeniDB.getSliverList(False, True, True)
      for sliv in slivers:
        fspecs = sliv.getFlowspecs()
        for fs in fspecs:
          for vlanid in fs.getVLANs():
            if vlanid not in used_vlans:
              used_vlans.append(vlanid)
      used_vlans.sort()
		
      if (use_json == True):
        return jsonify({"allocated-vlans" : used_vlans})
      else:
        return used_vlans		
	
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg = traceback.format_exc())

  #Vasileios: adapt vlanController.get_allocated_vlans_sorted method
  @route('/core/admin/list-allocated-vlans-sorted', methods=["POST", "GET"])
  def adminListAllocatedVlansSorted(self): #use_json = True
    #if not request.json:
    #  return
    try:		
      used_vlans = self.adminListAllocatedVlans(False)
      sorted_vlans = [0 for x in xrange(4)]
      sorted_vlans[0] = [x for x in used_vlans if x <= 1000]
      sorted_vlans[1] = [x for x in used_vlans if x > 1000 and x <= 2000]
      sorted_vlans[2] = [x for x in used_vlans if x > 2000 and x <= 3000]
      sorted_vlans[3] = [x for x in used_vlans if x > 3000]
		
      #if (use_json == True):
      return jsonify({"allocated-vlans-sorted" : sorted_vlans})
      #else:
      #  return sorted_vlans
	
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg = traceback.format_exc())

  #Vasileios: adapt vlanController.offer_vlan_tags method
  @route('/core/admin/offer-vlan-tags', methods=["POST", "GET"])
  def adminOfferVlanTags(self, set=None, use_json = True):
    if use_json == True:
      if not request.json:
        return
    try:
      if use_json == True:
        self.validate(request.json, [("vlan_set", (int))])
        vlan_set = request.json["vlan_set"]
      else:
        vlan_set = 0
      if use_json == True: #use json arg     
        if vlan_set == 0:
          returnval = [x for x in range(1,4095) if x not in self.adminListAllocatedVlans(False) and x not in locsettings.UNALLOWED_VLANS]
        elif vlan_set in range(1,4095):
          returnval = [x for x in range(1,4095) if x not in self.adminListAllocatedVlans(False) and x not in locsettings.UNALLOWED_VLANS][:vlan_set]
        else:
          returnval = None
      else: #override json arg
        if set in range(1,4095):
          returnval = [x for x in range(1,4095) if x not in self.adminListAllocatedVlans(False) and x not in locsettings.UNALLOWED_VLANS][:set]
        else:
          returnval = None
      if (use_json == True):
        return jsonify({"offered-vlan-tags" : returnval})
      else:
        return returnval
		
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg = traceback.format_exc())

  @route('/core/admin/expedient-stamp-fs-with-vlan', methods=["POST", "GET"])
  def expedientStampFSwithVlan(self):
    try:
      THIS_SITE_TAG = ConfigDB.getConfigItemByKey("geni.site-tag").getValue()
      filedir = './opt/ofelia/ofam/local/db'
      filename = os.path.join(filedir, 'expedient_slices_info.json')
      if os.path.isfile(filename):
        f = open(filename, 'r')
        slice_info_dict = json.load(f)
        f.close()
        self.validate(request.json, [("urn", (str)), ("vlan_stamp_start", (int)), ("vlan_stamp_end", (int))])
        slice_id = request.json["urn"].split("+slice+")[1].split(":")[0].split("id_")[1].split("name_")[0]      
        vlan_stamp_start = request.json["vlan_stamp_start"]
        vlan_stamp_end = request.json["vlan_stamp_end"]
        if (slice_id == "") or (slice_id not in slice_info_dict): 
          self._log.exception("The slice id you have specified is non-existent")
          raise Exception
        if vlan_stamp_start == 0:
          self._log.exception("You must provide a valid vlan stamp! Be careful with the provision, it is up to you")
          raise Exception
        updated_slice_info_dict = slice_info_dict.copy()
        for sliv_pos, sliver in enumerate(slice_info_dict[slice_id]['switch_slivers']):
          for sfs_pos, sfs in enumerate(sliver['flowspace']):   
            updated_slice_info_dict[slice_id]['switch_slivers'][sliv_pos]['flowspace'][sfs_pos]['vlan_id_start'] = vlan_stamp_start
            updated_slice_info_dict[slice_id]['switch_slivers'][sliv_pos]['flowspace'][sfs_pos]['vlan_id_end'] = vlan_stamp_end
        all_efs = self.create_slice_fs(updated_slice_info_dict[slice_id]['switch_slivers'])
        slice_of_rspec = create_ofv3_rspec(slice_id, updated_slice_info_dict[slice_id]['project_name'], updated_slice_info_dict[slice_id]['project_desc'], \
                                      updated_slice_info_dict[slice_id]['slice_name'], updated_slice_info_dict[slice_id]['slice_desc'], \
                                      updated_slice_info_dict[slice_id]['controller_url'], updated_slice_info_dict[slice_id]['owner_email'], \
                                      updated_slice_info_dict[slice_id]['owner_password'], \
                                      updated_slice_info_dict[slice_id]['switch_slivers'], all_efs)
        self._log.info(slice_of_rspec) #print the new rspec in the log for debugging
        #form the slice URN according to http://groups.geni.net/geni/wiki/GeniApiIdentifiers
        slice_urn = "urn:publicid:IDN+openflow:foam:"+ str(THIS_SITE_TAG) +"+slice+" + "id_" + str(slice_id) + "name_" + str(updated_slice_info_dict[slice_id]['slice_name'])
        creds = [] #creds are not needed at least for now: to be fixed
        user_info = {}
        user_info["urn"] = "urn:publicid:IDN+openflow:foam"+ str(THIS_SITE_TAG) +"+ch+" + "user+" + str(updated_slice_info_dict[slice_id]['owner_email']) #temp hack
        user_info["email"] = str(updated_slice_info_dict[slice_id]['owner_email'])
        old_exp_shutdown_success = self.gapi_DeleteSliver(slice_urn, creds, [])
        creation_result = self.gapi_CreateSliver(slice_urn, creds, slice_of_rspec, user_info)
        #store updated dict as a json file in foam db folder
        filedir = './opt/ofelia/ofam/local/db'
        filename = os.path.join(filedir, 'expedient_slices_info.json')
        tempfilename = os.path.join(filedir, 'expedient_slices_info.json.temp.' + str(time.time()) + str(random.randint(1,10000)))
        f = open(tempfilename, 'w')
        json.dump(updated_slice_info_dict, f)
        f.close()
        os.rename(tempfilename, filename)
        return jsonify({"slice-stamped" : "yes"})
      else:
        self._log.exception("The expedient slice info dict file is non-existent!")
        raise Exception
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg = traceback.format_exc())
  
  def get_direction(self, direction):
    if (direction == 'ingress'):
      return 0
    if (direction == 'egress'):
      return 1
    if (direction == 'bidirectional'):
      return 2
    return 2
  
  def create_slice_fs(self, switch_slivers):
    #legacy create slice flowspaces
    all_efs = [] 
    for sliver in switch_slivers:
      if "datapath_id" in sliver:
        dpid = sliver['datapath_id']
      else:
        dpid = "00:" * 8
        dpid = dpid[:-1]
          
      if len(sliver['flowspace'])==0:
        efs = ExperimentFLowSpace()
        #efs.exp  = e
        efs.dpid = dpid
        efs.direction = 2
        all_efs.append(efs)
      else:
        for sfs in sliver['flowspace']:
          efs = ExperimentFLowSpace()
          #efs.exp  = e
          efs.dpid = dpid
          if "direction" in sfs:
              efs.direction = self.get_direction(sfs['direction'])
          else:
              efs.direction = 2       
          fs = self.convert_star(sfs)
          for attr_name,(to_str, from_str, width, om_name, of_name) in \
          om_ch_translate.attr_funcs.items():
              ch_start ="%s_start"%(attr_name)
              ch_end ="%s_end"%(attr_name)
              om_start ="%s_s"%(om_name)
              om_end ="%s_e"%(om_name)
              setattr(efs,om_start,from_str(fs[ch_start]))
              setattr(efs,om_end,from_str(fs[ch_end]))
          all_efs.append(efs)
    return all_efs  

  def convert_star(self, fs):
    temp = fs.copy()
    for ch_name, (to_str, from_str, width, om_name, of_name) in \
    om_ch_translate.attr_funcs.items():
      ch_start = "%s_start" % ch_name
      ch_end = "%s_end" % ch_name
      if ch_start not in fs or fs[ch_start] == "*":
        temp[ch_start] = to_str(0)
      if ch_end not in fs or fs[ch_end] == "*":
        temp[ch_end] = to_str(2**width - 1)
    return temp

  def gapi_CreateSliver(self, slice_urn, credentials, rspec, users, force_approval=False, options=None):	
    #GENI API imports
    from foam.geni.db import GeniDB, UnknownSlice, UnknownNode
    import foam.geni.approval
    import foam.geni.ofeliaapproval
    import sfa
    user_info = users
    try:
      if True:
        #self.recordAction("createsliver", credentials, slice_urn)
        try:
          self._log.debug("Parsed user cert with URN (%(urn)s) and email (%(email)s)" % users)
        except Exception, e:
          self._log.exception("UNFILTERED EXCEPTION")
          user_info["urn"] = None
          user_info["email"] = None
        sliver = foam.geni.lib.createSliver(slice_urn, credentials, rspec, user_info)
        style = ConfigDB.getConfigItemByKey("geni.approval.approve-on-creation").getValue()
        if style == foam.geni.approval.NEVER:
          approve = False
        elif style == foam.geni.approval.ALWAYS:
          approve = True
        else:
          approve = foam.geni.ofeliaapproval.of_analyzeForApproval(sliver)
        if approve or force_approval:
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
    except Exception, e:
      self._log.exception("Exception")
      raise e
		  
  def gapi_DeleteSliver(self, slice_urn, credentials, options=None):
    #GENI API imports
    from foam.geni.db import GeniDB, UnknownSlice, UnknownNode
    import foam.geni.approval
    import foam.geni.ofeliaapproval
    import sfa
    try:
      if True:
        #self.recordAction("deletesliver", credentials, slice_urn)
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
	
  @route('/core/admin/enable-vlan-assignment-automation', methods=["POST", "GET"])
  def enableVlanAssignmentAutomation(self):
    self.vlan_automation_on = True
    return jsonify({"Vlan Assignment Automation" : "on"})

  @route('/core/admin/disable-vlan-assignment-automation', methods=["POST", "GET"])
  def disableVlanAssignmentAutomation(self):
    self.vlan_automation_on = False
    return jsonify({"Vlan Assignment Automation" : "off"})

  #VLAN handling code-base end

def setup (app):
  api = AdminAPIv1(app)
  return api

