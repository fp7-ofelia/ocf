# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University

import logging
import traceback
import time

from foam.core.json import jsonify, JSONValidationError, jsonValidate
from foam.api.jsonrpc import Dispatcher, route

class DebugAPIv1(Dispatcher):
  def __init__ (self, app):
    super(DebugAPIv1, self).__init__("Debug v1", app.logger, app)
    self._log.info("Loaded")

  @route('/core/debug/start-coverage', ["GET"])
  def startCoverage (self):
    try:
      import figleaf
      self._log.info("Starting coverage tracking")
      figleaf.start()
      return jsonify(None)
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/debug/stop-coverage', ["GET"])
  def stopCoverage (self):
    try:
      import figleaf
      figleaf.stop()
      self._log.info("Coverage tracking stopped")
      path = "/opt/ofelia/ofam/log/figleaf.%f.log" % (time.time())
      figleaf.write_coverage(path)
      self._log.info("Coverage written to %s" % (path))
      return jsonify({"output-path" : path})
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/debug/start-trace', ["GET"])
  def startTrace (self):
    try:
      from foam.core.tracer import Tracer
      self._log.info("Tracing enabled")
      Tracer.enable()
      return jsonify(None)
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/debug/stop-trace', ["GET"])
  def stopTrace (self):
    try:
      from foam.core.tracer import Tracer
      path = Tracer.disable()
      self._log.info("Tracing disabled")
      return jsonify({"output-path" : path})
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())


def setup (app):
  api = DebugAPIv1(app)
