# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University

from foam.core import json

class EventType(json.JSONInput):
  def __init__ (self, evt):
    import foam.events
    ev = foam.events.Type
    self.type_id = getattr(ev, evt)

  @staticmethod
  def validate (obj):
    import foam.events
    ev = foam.events.Type
    try:
      getattr(ev, obj)
      return True
    except AttributeError:
      return False

  @staticmethod
  def construct (obj):
    return EventType(obj)

  def __int__ (self):
    return self.type_id

