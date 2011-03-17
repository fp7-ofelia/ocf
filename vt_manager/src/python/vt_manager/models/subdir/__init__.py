import os
import re
import types
import unittest

MODEL_RE = r"^.*.py$"

# Search through every file inside this package.
model_names = []
model_dir = os.path.dirname( __file__)
PACKAGE = 'vt_manager.'+model_dir[model_dir.index('models'):].replace('/','.')
for filename in os.listdir(model_dir):
  if os.path.isdir(model_dir + "/" + filename):
    exec "from %s import %s" % (PACKAGE, filename)
  if not re.match(MODEL_RE, filename) or filename == "__init__.py":
    continue
  # Import the model file and find all clases inside it.
  model_module = __import__('%s.%s' % (PACKAGE, filename[:-3]),
                           {}, {},
                           filename[:-3])
  for name in dir(model_module):
    item = getattr(model_module, name)
    if not isinstance(item, (type, types.ClassType)):
      continue
    # Found a model, bring into the module namespace.
    exec "%s = item" % name
    exec "from %s.%s import %s" % (PACKAGE, filename[:-3], name)
    model_names.append(name)

