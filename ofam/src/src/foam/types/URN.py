from foam.core import json

class SliverURN(json.JSONInput):
  @staticmethod
  def validate (obj):
    if not isinstance(obj, (str, unicode)):
      return False
    return True

  @staticmethod
  def construct (obj):
    return str(obj)
