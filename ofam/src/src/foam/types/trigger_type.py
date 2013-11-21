# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University

from foam.core import json

class TriggerType(json.JSONInput):
  def __init__ (self, typ):
    import foam.events
    ev = foam.events.Event
    self.type_id = getattr(ev, typ)

  @staticmethod
  def validate (obj):
    import foam.events
    ev = foam.events.Event
    try:
      getattr(ev, obj)
      return True
    except AttributeError:
      return False

  @staticmethod
  def construct (obj):
    return TriggerType(obj)

  def __int__ (self):
    return self.type_id

