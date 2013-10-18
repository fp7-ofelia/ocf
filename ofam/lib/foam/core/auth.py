# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University

from foam.core.exception import CoreException

class NoMatchingPrivilege(CoreException):
  def __init__ (self, attrs):
    super(NoMatchingPrivilege, self).__init__()
    if isinstance(attrs, Attribute):
      self._attrs = [attrs]
    else:
      self.__attrs = attrs
  def __str__ (self):
    return "No available privilege satisfies request (%s)" % (
            ", ".join([x.name for x in self.__attrs]))


class User(object):
  def __init__ (self):
    self.id = None
    self.name = None
    self.email = None
    self._attrs = None
    self._keys = []

  def _assertPrivilege (self, attrs):
    if self._attrs is not None:
      if isinstance(attrs, Attribute):
        attrs = [attrs]
      for attr in attrs:
        if attr in self._attrs:
          return
    raise NoMatchingPrivilege(attrs)

  def _loadAssertPrivilege (self, attrs):
    from foam.core.configdb import ConfigDB
    self._attrs = set(DB.getUserAttributes(self.id))
    self.assertPrivilege = self._assertPrivilege
    return self.assertPrivilege(attrs)

  assertPrivilege = _loadAssertPrivilege

  def __eq__ (self, other):
    return self.id == other.id

  def setAttribute (self, attr):
    from foam.core.configdb import ConfigDB
    if attr not in self._attrs:
      self._attrs.add(attr)
      DB.setUserAttribute(self.id, attr.id)

  def getAttributes (self):
    from foam.core.configdb import ConfigDB
    if self._attrs is None:
      self._attrs = set(DB.getUserAttributes(self.id))
    return [x for x in self._attrs]


class Attribute(object):
  def __init__ (self, name=None, desc=""):
    self.id = None
    self.name = name
    self.desc = desc

  def __json__ (self):
    return {"id" : self.id, "name" : self.name, "desc" : self.desc}

  def __eq__ (self, other):
    return self.id == other.id


class SuperUser(User):
  def __init__ (self):
    super(SuperUser, self).__init__()

  def assertPrivilege (self, attrs):
    return
  


