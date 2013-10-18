# Copyright (c) 2012  Nick Bastin

from flask import request

from foam.api.jsonrpc import Dispatcher, route
from foam.config import HTPASSWDFILE
from foam.core.configdb import ConfigDB, UnknownAttributeName
from foam.core.htpasswd import HtpasswdFile
from foam.core.auth import Attribute, NoMatchingPrivilege
from foam.core.json import jsonify, jsonValidate, JSONValidationError

class AuthAPIv1(Dispatcher):
  def __init__ (self, app):
    super(AuthAPIv1, self).__init__("Auth v1", app.logger, app)
    self._log.info("Loaded")
    self._htp = HtpasswdFile(HTPASSWDFILE)
    self.attrSetAdminPasswd = self.createAttribute(Attribute("auth.admin.setpasswd"))

  def validate (self, rjson, types):
    return jsonValidate(rjson, types, self._log)

  def createAttribute (self, attr):
    try:
      return ConfigDB.getAttributeByName(attr.name)
    except UnknownAttributeName, e:
      self._log.info("Creating attribute: %s" % (attr.name))
      ConfigDB.createAttribute(attr)
      self._log.debug("Created attribute [%s] with ID %d" % (attr.name, attr.id))
      return attr

  @route('/core/auth/set-admin-passwd', methods=["POST"])
  def setAdminPasswd (self):
    if not request.json:
      return
    try:
      u = ConfigDB.getUser(request.environ["USER"])
      u.assertPrivilege(self.attrSetAdminPasswd)

      opts = self.validate(request.json, [("passwd", (unicode, str))])

      self._log.info("Updating foamadmin password")
      self._htp.update("foamadmin", opts["passwd"])
      self._htp.save()

      return jsonify(None)
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except NoMatchingPrivilege, e:
      return jsonify(str(e), code = 2, msg = str(e))

def setup (app):
  api = AuthAPIv1(app)
  return api
