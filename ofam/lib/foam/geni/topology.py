# Copyright (c) 2012 Barnstormer Softworks

import logging
import uuid

from foam.core.exception import CoreException
from foam.core.log import KeyAdapter

class IllegalAttachmentsValue(CoreException):
  def __init__ (self, newval):
    self.val = newval
  def __str__ (self):
    return "Tried to set attachments config to illegal value: %s" % (self.val)

class Attachment(object):
  def __init__ (self):
    self.uuid = None
    self.dpid = None
    self.remote_component_id = None
    self.remote_port = None
    self.local_port = None
    self.desc = None


class _TopoDB(object):
  def __init__ (self):
    self._log = KeyAdapter("GENI-TopoDB", logging.getLogger("foam"))
    self._attachments = ConfigDB.getConfigItemByKey("site.attachments").getValue()
    self._attachmentsByDPID = {}
    for k,v in self._attachments.iteritems():
      self._attachmentsByDPID.getdefault(v.dpid, []).append(v)

  def addAttachment (self, dpid, attachment):
    attachment.dpid = dpid
    self._attachments[attachment.uuid] = attachment
    self._attachmentsByDPID.getdefault(dpid, {}).getdefault(attachment.local_port, []).append(attachment)
    self.writeAttachments()

  def writeAttachments (self):
    ConfigDB.getConfigItemByKey("site.attachments").write(self._attachments)

  def listAttachments (self):
    return self._attachments.values()

  def getDPIDAttachments (self, dpid):
    try:
      return self._attachmentsByDPID[dpid]
    except KeyError, e:
      return {}

  def getAttachment (self, aid):
    return self._attachments[aid]

def updateAttachments (key, newval):
  if type(newval) is not dict:
    raise IllegalAttachmentsValue(newval)
  return newval


from foam.core.configdb import ConfigDB

TopoDB = _TopoDB()


