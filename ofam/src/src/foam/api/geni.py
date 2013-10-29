# Copyright (c) 2012  Nick Bastin

import traceback
import datetime

from flask import request

from foam.config import FOAM_ROOT
from foam.api.jsonrpc import Dispatcher, route
from foam.core.json import jsonify, jsonValidate, JSONValidationError
from foam.core.configdb import ConfigDB, ConfigItem
from foam.geni.topology import Attachment, TopoDB
from foam.geni.approval import AppData


class GENIAPIv1(Dispatcher):
  def __init__ (self, app):
    super(GENIAPIv1, self).__init__("GENI v1", app.logger, app)
    self._log.info("Loaded")
    self.appdata = AppData

  def validate (self, rjson, types):
    return jsonValidate(rjson, types, self._log)

  @route('/geni/approval/get-macs', methods=['GET'])
  def getMACs (self):
    return jsonify([x for x in AppData.iterMACs()])

  @route('/geni/approval/get-ethertypes', methods=['GET'])
  def getEthertypes (self):
    return jsonify([x for x in AppData.iterEthertypes()])

  @route('/geni/approval/get-subnets', methods=['GET'])
  def getSubnets (self):
    return jsonify([x for x in AppData.iterSubnets()])

  @route('/geni/approval/rebuild-db', methods=["GET"])
  def rebuildDB (self):
    AppData.rebuild()
    return jsonify(None)

  @route('/geni/approval/add-user-urn', methods=["POST"])
  def addUserURN (self):
    if not request.json:
      return
    try:
      objs = self.validate(request.json, [("urn", (unicode, str))])
      u = ConfigDB.getUser(request.environ["USER"])
      AppData.addUserURN(objs["urn"], u)
      return jsonify(None)
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/geni/approval/remove-user-urn', methods=["POST"])
  def removeUserURN (self):
    if not request.json:
      return
    try:
      objs = self.validate(request.json, [("urn", (unicode, str))])
      u = ConfigDB.getUser(request.environ["USER"])
      AppData.removeUserURN(objs["urn"], u)
      return jsonify(None)
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/geni/approval/list-user-urns', methods=["GET"])
  def listUserURNs (self):
    try:
      u = ConfigDB.getUser(request.environ["USER"])
      return jsonify(list(ConfigDB.getConfigItemByKey("geni.approval.user-urns").getValue(u)))
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg = traceback.format_exc())

  @route('/geni/approval/create-port-group', methods=["POST"])
  def createPortGroup (self):
    if not request.json:
      return
    try:
      objs = self.validate(request.json, [("name", (unicode, str)),
                                          ("desc", (unicode, str))])
      u = ConfigDB.getUser(request.environ["USER"])
      pg = AppData.createPortGroup(objs["name"], objs["desc"])
      return jsonify(str(pg.uuid))
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/geni/approval/add-port', methods=["POST"])
  def addPortToGroup (self):
    if not request.json:
      return
    try:
      objs = self.validate(request.json, [("group-id", (unicode, str)),
                                          ("dpid", (unicode, str)),
                                          ("port-num", (int))])
      pg = AppData.getPortGroup(objs["group-id"])
      pg.addPort(objs["dpid"], objs["port-num"])
      return jsonify(None)
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/geni/approval/remove-port', methods=["POST"])
  def removePortFromGroup (self):
    if not request.json:
      return
    try:
      objs = self.validate(request.json, [("group-id", (unicode, str)),
                                          ("dpid", (unicode, str)),
                                          ("port-num", (int))])
      pg = AppData.getPortGroup(objs["group-id"])
      pg.removePort(objs["dpid"], objs["port-num"])
      return jsonify(None)
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/geni/approval/list-port-groups', methods=["GET"])
  def listPortGroups (self):
    try:
      groups = AppData.getPortGroups()
      l = [str(x) for x in groups.keys()]
      return jsonify(l)
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/geni/approval/show-port-group', methods=["POST"])
  def showPortGroup (self):
    if not request.json:
      return
    try:
      objs = self.validate(request.json, [("group-id", (unicode, str))])
      pg = AppData.getPortGroup(objs["group-id"])
      return jsonify(pg)
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/geni/topology/create-attachment', methods=["POST"])
  def createAttachment (self):
    return jsonify(None)

  @route('/geni/topology/remove-attachment', methods=["POST"])
  def removeAttachment (self):
    return jsonify(None)

  @route('/geni/topology/list-attachments', methods=["GET"])
  def listAttachments (self):
    return jsonify(None)
  
  #Nick's code for handling VLANs (version 0.10 - MAINT)
  '''
  @route('/geni/approval/add-shared-vlan', methods=["POST"])
  def addSharedVLAN (self):
    if not request.json:
      return
    try:
      objs = self.validate(request.json, [("vlan-id", (int))])
      u = ConfigDB.getUser(request.environ["USER"])
      self.appdata.addSharedVLAN(objs["vlan-id"], u)
      return jsonify(None)
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/geni/approval/remove-shared-vlan', methods=["POST"])
  def removeSharedVLAN (self):
    if not request.json:
      return
    try:
      objs = self.validate(request.json, [("vlan-id", (int))])
      u = ConfigDB.getUser(request.environ["USER"])
      self.appdata.removeSharedVLAN(objs["vlan-id"], u)
      return jsonify(None)
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/geni/approval/list-shared-vlans', methods=["GET"])
  def listSharedVLANs (self):
    try:
      u = ConfigDB.getUser(request.environ["USER"])
      return jsonify(list(ConfigDB.getConfigItemByKey("geni.approval.shared-vlans").getValue(u)))
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg = traceback.format_exc())
    
  @route('/geni/approval/add-reserved-vlan', methods=["POST"])
  def addReservedVLAN (self):
    if not request.json:
      return
    try:
      objs = self.validate(request.json, [("vlan-id", (int))])
      u = ConfigDB.getUser(request.environ["USER"])
      self.appdata.addAdminVLAN(objs["vlan-id"], u)
      return jsonify(None)
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/geni/approval/remove-reserved-vlan', methods=["POST"])
  def removeReservedVLAN (self):
    if not request.json:
      return
    try:
      objs = self.validate(request.json, [("vlan-id", (int))])
      u = ConfigDB.getUser(request.environ["USER"])
      self.appdata.removeAdminVLAN(objs["vlan-id"], u)
      return jsonify(None)
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/geni/approval/list-reserved-vlans', methods=["GET"])
  def listReservedVLANs (self):
    try:
      u = ConfigDB.getUser(request.environ["USER"])
      return jsonify(list(ConfigDB.getConfigItemByKey("geni.approval.admin-vlans").getValue(u)))
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg = traceback.format_exc())
  '''

def setup (app):
  api = GENIAPIv1(app)
  return api
