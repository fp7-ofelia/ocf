# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University

import email
import email.parser
from email.mime.text import MIMEText
import smtplib
import imp

from foam import events
import foamext.triggers

class UnsupportedTriggerType(Exception):
  def __init__ (self, typ):
    self.type = typ
  def __str__ (self):
    return "Unsupport trigger type: %s" % (self.type)

class UnimplementedTrigger(Exception):
  def __init__ (self):
    pass

def getTriggerFunc (name):
  (modname, func) = name.split(".")
  try:
    (fp, pn, d) = imp.find_module(modname, foamext.triggers.__path__)
    mod = imp.load_module(modname, fp, pn, d)
    return getattr(mod, func)
  finally:
    if fp:
      fp.close()


# Triggers are copy.copy()'d, so if you need a different behaviour, make this safe
# by setting up your object specially, or implementing __copy__ as a caller of __deepcopy__

class Trigger(object):
  def __init__ (self, start, end, event, data):
    self._tr_start = getTriggerFunc(start)
    self._tr_end = getTriggerFunc(end)
    self._tr_event = event
    self._tr_action = data
    self._tr_state = None

  def execute (self):
    raise UnimplementedTrigger()

  def start_check (self, env):
    return self.__tr_start(env)

  def end_check (self, env):
    return self.__tr_end(env)

  def setState (self, key, value):
    if self._tr_state == None:
      self._tr_state = {}
    self._tr_state[key] = value

  def getState (self, key):
    if self._tr_state == None:
      self._tr_state = {}
    return self._tr_state[key]

  def hasState (self, key = None):
    if key == None:
      if self._tr_state == None or len(self._tr_state) == 0:
        return False
    if self._tr_state == None:
      self._tr_state = {}
    return key in self._tr_state

  @staticmethod
  def construct (typ, start, end, event, data):
    if typ == Events.Type.EMAIL:
      return Email(start, end, event, data)
    elif typ == Events.Type.CALLBACK:
      return Callback(start, end, event, data)
    else:
      raise UnsupportTriggerType(typ)


class Email(Trigger):
  def __init__ (self, start, end, event, action):
    super(Email, self).__init__(start, end, event, data)
    self.__event = event
    self.__info = data
    self.__state = None

    self._tmpl = open(data["template"], "r").read()


  def setHeader (self, hdr, keys):
    if self.__info.has_key(hdr):
      self._msg[hdr] = self.__info[hdr] % (keys)

  def execute (self, env):
    s = smtplib.SMTP(self.__info['server'])
    keys = self.convertEnv(env)

    tmpl = self._tmpl % (keys)
    msg = email.parser.Parser().parsestr(tmpl)

    self.setHeader("To", keys)
    self.setHeader("From", keys)
    self.setHeader("Subject", keys)

    s.sendmail(self._msg['From'], self._msg['To'], msg)
    s.quit()


class Callback(object):
  def __init__ (self, start, end, event, action):
    super(Callback, self).__init__(start, end, event, data)


class TriggerBag(object):
  def __init__ (self):
    self.__bag = []

  def insert (self, trigger):
    self.__bag.append(trigger)

  def execute (self, env):
    for t in self.__bag:
      if t.end_check(env):
        t.execute(env)


class _EventManager(object):
  def __init__ (self):
    self.__triggers = {}

  def loadTriggers (self):
    from foam import db
    s = db.select([db.triggers])
    conn = db.db_session.connection()
    res = conn.execute(s)
    for row in res:
      action = row[db.triggers.c.action]
      self.__triggers.setdefault(row[db.triggers.c.event], []).append(
          Trigger.construct(action["type"],
                            row[db.triggers.c.start_test],
                            row[db.triggers.c.end_test],
                            row[db.triggers.c.event],
                            action["data"]))

  def prepEvent (self, event, data):
    triggers = self.__triggers.get(event, [])
    filtered = TriggerBag()
    for trigger in triggers:
      t = copy.copy(trigger)
      if t.start_check(data):
        filtered.insert(t)
    return filtered

EventManager = _EventManager()
EventManager.loadTriggers()
