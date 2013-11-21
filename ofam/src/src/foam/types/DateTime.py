# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University

import datetime

from foam.core import json

_ZERO = datetime.timedelta(0)

class FixedOffsetTZ(datetime.tzinfo):
  def __init__ (self, offset=0, name="UTC"):
    self.__offset = datetime.timedelta(minutes = offset)
    self.__name = name

  def utcoffset (self, dt):
    return self.__offset

  def tzname (self, dt):
    return self.__name

  def dst (self, dt):
    return _ZERO

UTC = FixedOffsetTZ(0, "UTC")


class DateTime(json.JSONInput):
  @staticmethod
  def validate (obj):
    if not isinstance(obj, (int, float)):
      return False
    return True

  @staticmethod
  def construct (obj):
    return datetime.datetime.fromtimestamp(obj, UTC)

