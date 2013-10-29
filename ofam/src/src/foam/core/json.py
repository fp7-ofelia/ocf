# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University

from flask import Response, json

from foam.core.exception import CoreException

class NotImplemented(CoreException):
  def __init__ (self):
    pass
  def __str__ (self):
    return "Specified input type lacks JSON constructor."

class JSONInput(object):
  def validate (self, obj):
    return False

  def construct (self, obj):
    raise NotImplemented

class JSONValidationError(CoreException):
  def __init__ (self, fields):
    super(JSONValidationError, self).__init__()
    self.code = 2
    self.__fields = fields

  def __json__ (self):
    return {"exception" : "JSON Parse Error: expected fields were missing and/or of the wrong type",
         "missing" : ["%s: %s" % (n,str(t)) for (p,n,t) in self.__fields if not p],
         "wrong-type" : ["%s: %s" % (n, str(t)) for (p,n,t) in self.__fields if p]}

  def __str__ (self):
    return "JSON Parse Error: expected fields were missing and/or of the wrong type"

class APIEncoder(json.JSONEncoder):
  def default (self, obj):
    try:
      return obj.__json__()
    except AttributeError, e:
      return json.JSONEncoder.default(self, obj)

def jsonify (data, code = 0, msg = ""):
  retstruct = { "retcode" : code, "msg" : msg, "value" : data }
  return Response(json.dumps(retstruct, cls=APIEncoder), mimetype='application/json')

def jsonValidate (obj, fields, logger):
  fail = []
  out_objs = {}
  for (name, typ) in fields:
    if not obj.has_key(name):
      fail.append((False, name, typ))
    if typ is not None:
      if isinstance(typ, tuple):
        if not isinstance(obj[name], typ):
          logger.warning("[%s] %s, expected %s" % (name, type(obj[name]), typ))
          fail.append((True, name, typ))
        else:
          out_objs[name] = obj[name]
      elif issubclass(typ, JSONInput):
        if not typ.validate(obj[name]):
          logger.warning("[%s] %s, expected %s" % (name, type(obj[name]), typ))
          fail.append((True, name, typ))
        else:
          out_objs[name] = typ.construct(obj[name])
      else:
        out_objs[name] = obj[name]
  if fail:
    raise JSONValidationError(fail)
  return out_objs

