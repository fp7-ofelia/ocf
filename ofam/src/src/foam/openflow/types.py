# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University
# Copyright (c) 2012  Barnstormer Softworks, Ltd.

from foam.core.exception import CoreException

class MergeDPIDMismatch(object):
  def __init__ (self, a, b):
    super(MergeDPIDMismatch, self).__init__()
    self.a = a
    self.b = b
  def __str__ (self):
    return "Attempt to merge mismatched datapaths: %s, %s" % (self.a, self.b)

class Port(object):
  def __init__ (self):
    self.name = None
    self.num = None
    self.features = None
    self.__dpid = None

  @property
  def dpid (self):
    return self.__dpid

  @dpid.setter
  def dpid (self, value):
    self.__dpid = value.lower()

  def __str__ (self):
    return "[%d] %s" % (self.num, self.name)

  def __hash__ (self):
    return hash("%s-%d" % (self.dpid, self.num))

  def __json__ (self):
    return { "num" : self.num, "name" : self.name, "dpid" : self.dpid }

  def __cmp__ (self, other):
    if self.dpid == other.dpid:
      if self.num < other.num:
        return -1
      elif self.num == other.num:
        return 0
      elif self.num > other.num:
        return 1
    elif self.dpid < other.dpid:
      return -1
    elif self.dpid > other.dpid:
      return 1


class Datapath(object):
  def __init__ (self):
    self.dpid = None
    self.ports = set()

  def __str__ (self):
    return "[%s] %s\n" % (self.dpid,
        "    ".join(["%s" % (str(x)) for x in self.ports]))

  def __json__ (self):
    return {"dpid" : self.dpid,
            "ports" : [x.__json__() for x in self.ports]}

  #TODO: Should this return a new datapath?
  def merge (self, other):
    if self.dpid != other.dpid:
      raise MergeDPIDMismatch(self.dpid, other.dpid)

    if (len(other.ports) == 0) or (len(self.ports) == 0):
      self.ports = set()
      return

    for p in other.ports:
      self.ports.add(p)

  def addPort (self, port):
    self.ports.add(port)


class Controller(object):
  TYPES = set(["primary", "backup", "monitor"])

  def __init__ (self):
    self.type = None
    self.url = None

  def __str__ (self):
    return "%s: %s" % (self.type, self.url)

  def __json__ (self):
    return {"type" : self.type, "url" : self.url}
