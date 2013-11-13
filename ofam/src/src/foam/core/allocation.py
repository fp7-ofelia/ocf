# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University
import uuid
import datetime

from foam.lib import _asUTC

class Allocation(object):
  def __init__ (self, exp = None):
    self._uuid = uuid.uuid4()
    self._email = None
    self._description = None
    self._creationTime = _asUTC(datetime.datetime.utcnow())
    self._expireEmailStatus = { "day" : False, "week" : False }

  def __str__ (self):
    return "<Allocation: %s, %s,\n  %s>" % (self._uuid,
      str(self._email), self._description)

  def getDataDict (self, detail = True):
    obj = {"desc" : self._description, "email" : self._email,
           "uuid" : str(self._uuid) }
    return obj

  def getUUID (self):
    return self._uuid

  def setEmail (self, email):
    self._email = email

  def getEmail (self):
    return self._email

  def setDescription (self, desc):
    self._description = desc

  def getDescription (self):
    return self._description
  
  def resetExpireEmail (self):
    self._expireEmailStatus = { "day" : False, "week" : False }

  def getEmailStatus (self, key):
    return self._expireEmailStatus[key]

  def setEmailStatus (self, key, value = True):
    self._expireEmailStatus[key] = value

  def getCreationDate (self):
    return self._creationTime
