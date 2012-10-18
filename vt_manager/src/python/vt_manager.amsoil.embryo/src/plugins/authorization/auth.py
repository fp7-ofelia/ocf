import os.path

try:
  import cPickle as pickle
except ImportError:
  import pickle


from amsoil.core.exception import CoreException
import amsoil.core.mutex as MTXSVC


class UnknownAttributeName(CoreException):
  def __init__ (self, name):
    super(UnknownAttributeName, self).__init__()
    self.name = name
  def __str__ (self):
    return "Attempted to reference unknown attribute '%s'" % (self.name)

class UnknownAttributeID(CoreException):
  def __init__ (self, aid):
    super(UnknownAttributeID, self).__init__()
    self.aid = aid 
  def __str__ (self):
    return "Attempted to reference unknown attribute with ID %d" % (self.aid)

class UnknownUser(CoreException):
  def __init__ (self, name):
    super(UnknownUser, self).__init__()
    self.name = name
  def __str__ (self):
    return "Attempted to reference unknown user '%s'" % (self.name)

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

class Context(object):
  def __init__ (self):
    self.user = None
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
    self._attrs = set(AttrDB.getUserAttributes(self.user))
    self.assertPrivilege = self._assertPrivilege
    return self.assertPrivilege(attrs)

  assertPrivilege = _loadAssertPrivilege
  assertPrivilege.__doc__ = """
  Assert that this context contains one of the privileges specified.

  Returns None on success, raises NoMatchingPrivilege on failure.
"""

  def __eq__ (self, other):
    return self.user == other.user

  def setAttribute (self, attr, persist=False):
    """Adds the given attribute to this context for future privilege checks.
      If persist is True, also writes the attribute into persistent storage
      for all future checks against contexts created for this user."""
    if attr not in self._attrs:
      self._attrs.add(attr)
      if persist:
        AttrDB.setUserAttribute(self.user, attr.id)

  def getAttributes (self):
    if self._attrs is None:
      self._attrs = set(AttrDB.getUserAttributes(self.user))
    return [x for x in self._attrs]


class Attribute(object):
  def __init__ (self, name=None, desc=""):
    self.name = name
    self.desc = desc

  def __json__ (self):
    return {"name" : self.name, "desc" : self.desc}

  def __eq__ (self, other):
    return self.name == other.name

  def setName (self, name):
    self.name = name
    return self

  def setDescription (self, desc):
    self.desc = desc
    return self


class SuperUser(Context):
  """Authorization context that has every privilege."""
  def __init__ (self):
    super(SuperUser, self).__init__()

  def assertPrivilege (self, attrs):
    return

class User(object):
  def __init__ (self):
    self.name = None
    self.email = None

  def setName (self, uname):
    self.name = uname
    return self

  def setEmail (self, email):
    self.email = email
    return self


class AttributeDB(object):
  DBPATH = "auth.db" # TODO put this in a config (if this database is needed, careful this plugin is required by the config plugin)

  def __init__ (self):
    if os.path.exists(AttributeDB.DBPATH):
      (self._attrs, self._users, self._user_attrs) = pickle.load(AttributeDB.DBPATH)
    else:
      self._attrs = {}
      self._users = {}
      self._user_attrs = {}

  def write (self):
    with MTXSVC.mutex("attrdb"):
      pickle.dump((self._attrs, self._users, self._user_attrs), AttributeDB.DBPATH)

  def setUserAttribute (self, user, attr):
    self._user_attrs.setdefault(user, set()).add(attr)
    self.write()

  def getUserAttributes (self, user):
    return self._user_attrs.setdefault(user, set())

  def addUser (self, uname, email=None):
    u = User().setName(uname).setEmail(email)
    self._users[u.name] = u

  def getUser (self, uname):
    return self._users[uname]

  def getAttribute (self, name):
    return self._attrs[name]

  def addAttribute (self, attr):
    self._attrs[attr.name] = attr


AttrDB = AttributeDB()

