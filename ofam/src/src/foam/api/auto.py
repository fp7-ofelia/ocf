# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University

import logging
import traceback
import datetime

from flask import request

from foam.core.json import jsonify
from foam.api.jsonrpc import Dispatcher, route
from foam.creds import TokenVerifier, TokenError
from foam.geni.db import GeniDB
from foam.lib import _asUTC

import foam.task
import foam.geni.lib

class AutoAPIv1(Dispatcher):
  def __init__ (self, app):
    super(AutoAPIv1, self).__init__("Auto v1", app.logger, app)
    self._log.info("Loaded")

  @route('/auto/approve-sliver', methods=["POST"])
  def autoApproveSliver (self):
    if not request.json:
      return
    try:
      TokenVerifier.checkToken("approve-sliver", request.json["sliver_urn"])
      return foam.geni.lib.approveSliver(request, self._log)
    except TokenError, e:
      return jsonify({"exception" : traceback.format_exc()})
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/auto/expire-slivers', methods=["GET"])
  def expireSlivers (self):
    now = _asUTC(datetime.datetime.utcnow())
    exc_stack = []
    expired_slivers = []

    try:
      slivers = GeniDB.getExpiredSliverList(now)
      for sliver in slivers:
        try:
          data = GeniDB.getSliverData(sliver["sliver_urn"], True)

          TokenVerifier.checkToken("expire-sliver", sliver["sliver_urn"])
          foam.geni.lib.deleteSliver(sliver_urn = sliver["sliver_urn"])

          foam.task.emailExpireSliver(data)
          expired_slivers.append(data["sliver_urn"])
        except TokenError, e:
          exc_stack.append(jsonify({"exception" : traceback.format_exc()}))
      return jsonify({"expired" : expired_slivers})
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg = traceback.format_exc())

  @route('/auto/expire-emails', methods=["GET"])
  def processExpirationEmails (self):
    now = _asUTC(datetime.datetime.utcnow())
    self._log.debug("Expiration check: %s" % (str(now)))
    day_alert = []
    week_alert = []
    try:
      slivers = GeniDB.getSliverList(False)
      for sliver in slivers:
        sobj = GeniDB.getSliverObj(sliver["sliver_urn"])
        (urn, action) = sobj.emailCheck(now)
        if action == 1:
          day_alert.append(urn)
          self._log.info("[%s] Sent email for expiry within 30 hours" % (urn))
        elif action == 2:
          week_alert.append(urn)
          self._log.info("[%s] Sent email for expiry within 7 days" % (urn))
        else:
          self._log.debug("[%s] Expiration check: No email required for sliver expiration (%s)" % (urn, sobj.getExpiration()))
      return jsonify({"status" : "success", "day_alerts" : day_alert, "week_alerts" : week_alert})
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/auto/email-queue', methods=["GET"])
  def emailPendingQueue (self):
    try:
      lines = []
      pending_list = GeniDB.getSliverList(False, None)
      for sliver in pending_list:
        sobj = GeniDB.getSliverObj(sliver["sliver_urn"])
        lines.append("Sliver URN: %s" % sobj.getURN())
        lines.append("     User: %s [%s]" % (sobj.getEmail(), sobj.getUserURN()))
        lines.append("")
      if lines:
        self._log.info("[Daily Queue] Sending email for %d sliver(s)" % (len(lines)/3))
        queue = "\n".join(lines)
        foam.task.emailPendingQueue({"pending-queue" : queue})
        return jsonify(None)
      self._log.info("[Daily Queue] No pending slivers to email")
      return jsonify(None)
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())


def setup (app):
  api = AutoAPIv1(app)
