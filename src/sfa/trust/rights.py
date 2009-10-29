##
# This Module implements rights and lists of rights for the Geni wrapper. Rights
# are implemented by two classes:
#
# Right - represents a single right
#
# RightList - represents a list of rights
#
# A right may allow several different operations. For example, the "info" right
# allows "listslices", "listcomponentresources", etc.
##

##
# privilege_table is a list of priviliges and what operations are allowed
# per privilege.

privilege_table = {"authority": ["register", "remove", "update", "resolve", "list", "getcredential"],
                   "refresh": ["remove", "update"],
                   "resolve": ["resolve", "list", "getcredential"],
                   "sa": ["getticket", "redeemslice", "createslice", "deleteslice", "updateslice", 
                          "getsliceresources", "getticket", "loanresources", "stopslice", "startslice", 
                          "deleteslice", "resetslice", "listslices", "listnodes", "getpolicy"],
                   "embed": ["getticket", "redeemslice", "createslice", "deleteslice", "updateslice", "getsliceresources"],
                   "bind": ["getticket", "loanresources"],
                   "control": ["updateslice", "createslice", "stopslice", "startslice", "deleteslice", "resetslice", "getsliceresources"],
                   "info": ["listslices", "listnodes", "getpolicy"],
                   "ma": ["setbootstate", "getbootstate", "reboot"]}


##
# Determine tje rights that an object should have. The rights are entirely
# dependent on the type of the object. For example, users automatically
# get "refresh", "resolve", and "info".
#
# @param type the type of the object (user | sa | ma | slice | node)
# @param name human readable name of the object (not used at this time)
#
# @return RightList object containing rights

def determine_rights(type, name):
    rl = RightList()

    # rights seem to be somewhat redundant with the type of the credential.
    # For example, a "sa" credential implies the authority right, because
    # a sa credential cannot be issued to a user who is not an owner of
    # the authority
    if type == "user":
        rl.add("refresh")
        rl.add("resolve")
        rl.add("info")
    elif type == "sa":
        rl.add("authority,sa")
    elif type == "ma":
        rl.add("authority,ma")
    elif type == "authority":
        rl.add("authority,sa,ma")
    elif type == "slice":
        rl.add("refresh")
        rl.add("embed")
        rl.add("bind")
        rl.add("control")
        rl.add("info")
    elif type == "component":
        rl.add("operator")
    return rl


##
# The Right class represents a single privilege.



class Right:
   ##
   # Create a new right.
   #
   # @param kind is a string naming the right. For example "control"

   def __init__(self, kind):
      self.kind = kind

   ##
   # Test to see if this right object is allowed to perform an operation.
   # Returns True if the operation is allowed, False otherwise.
   #
   # @param op_name is a string naming the operation. For example "listslices".

   def can_perform(self, op_name):
      allowed_ops = privilege_table.get(self.kind.lower(), None)
      if not allowed_ops:
         return False

      # if "*" is specified, then all ops are permitted
      if "*" in allowed_ops:
         return True

      return (op_name.lower() in allowed_ops)

   ##
   # Test to see if this right is a superset of a child right. A right is a
   # superset if every operating that is allowed by the child is also allowed
   # by this object.
   #
   # @param child is a Right object describing the child right

   def is_superset(self, child):
      my_allowed_ops = privilege_table.get(self.kind.lower(), None)
      child_allowed_ops = privilege_table.get(child.kind.lower(), None)

      if "*" in my_allowed_ops:
          return True

      for right in child_allowed_ops:
          if not right in my_allowed_ops:
              return False

      return True

##
# A RightList object represents a list of privileges.

class RightList:
    ##
    # Create a new rightlist object, containing no rights.
    #
    # @param string if string!=None, load the rightlist from the string

    def __init__(self, string=None):
        self.rights = []
        if string:
            self.load_from_string(string)

    def is_empty(self):
        return self.rights == []

    ##
    # Add a right to this list
    #
    # @param right is either a Right object or a string describing the right

    def add(self, right):
        if isinstance(right, str):
            right = Right(kind = right)
        self.rights.append(right)

    ##
    # Load the rightlist object from a string

    def load_from_string(self, string):
        self.rights = []

        # none == no rights, so leave the list empty
        if not string:
            return

        parts = string.split(",")
        for part in parts:
            self.rights.append(Right(part))

    ##
    # Save the rightlist object to a string. It is saved in the format of a
    # comma-separated list.

    def save_to_string(self):
        right_names = []
        for right in self.rights:
            right_names.append(right.kind)

        return ",".join(right_names)

    ##
    # Check to see if some right in this list allows an operation. This is
    # done by evaluating the can_perform function of each operation in the
    # list.
    #
    # @param op_name is an operation to check, for example "listslices"

    def can_perform(self, op_name):
        for right in self.rights:
            if right.can_perform(op_name):
                return True
        return False

    ##
    # Check to see if all of the rights in this rightlist are a superset
    # of all the rights in a child rightlist. A rightlist is a superset
    # if there is no operation in the child rightlist that cannot be
    # performed in the parent rightlist.
    #
    # @param child is a rightlist object describing the child

    def is_superset(self, child):
        for child_right in child.rights:
            allowed = False
            for my_right in self.rights:
                if my_right.is_superset(child_right):
                    allowed = True
            if not allowed:
                return False
        return True


    ##
    # Determine tje rights that an object should have. The rights are entirely
    # dependent on the type of the object. For example, users automatically
    # get "refresh", "resolve", and "info".
    #
    # @param type the type of the object (user | sa | ma | slice | node)
    # @param name human readable name of the object (not used at this time)
    #
    # @return RightList object containing rights

    def determine_rights(self, type, name):
        rl = RightList()

        # rights seem to be somewhat redundant with the type of the credential.
        # For example, a "sa" credential implies the authority right, because
        # a sa credential cannot be issued to a user who is not an owner of
        # the authority

        if type == "user":
            rl.add("refresh")
            rl.add("resolve")
            rl.add("info")
        elif type == "sa":
            rl.add("authority,sa")
        elif type == "ma":
            rl.add("authority,ma")
        elif type == "authority":
            rl.add("authority,sa,ma")
        elif type == "slice":
            rl.add("refresh")
            rl.add("embed")
            rl.add("bind")
            rl.add("control")
            rl.add("info")
        elif type == "component":
            rl.add("operator")

        return rl
