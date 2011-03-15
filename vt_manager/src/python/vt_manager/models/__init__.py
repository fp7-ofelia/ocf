import os
import re
import types
import unittest

##FIX: IT IS ONLY USEFUL IF MODELS IN SUBDIRECTORIES HAVE NO DEPENDENCIES WITH OTHER MODELS
#
#PACKAGE = 'vt_manager.models'
#MODEL_RE = r"^.*.py$"
#
## Search through every file inside this package.
#model_names = []
#model_subdir = []
#model_dir = os.path.dirname( __file__)
#
#for dirname in os.listdir(model_dir):
#  if os.path.isdir(os.path.join(model_dir, dirname)):
#    print dirname
#    model_subdir.append(os.path.join(model_dir,dirname))
#
#model_subdir.append(model_dir)
#print model_subdir
#for dirname in model_subdir:
#  for filename in os.listdir(dirname):
#    if not re.match(MODEL_RE, filename) or filename == "__init__.py":
#      continue
#    # Import tihe model file and find all clases inside it.
#    if dirname.split('/')[-1] == 'models':
#        subdir = ''
#    else:
#        subdir = dirname.split('/')[-1]+'.'
#    
#    model_module = __import__('%s.%s%s' % (PACKAGE, subdir,filename[:-3]),
#                             {}, {},
#                             filename[:-3])
#    for name in dir(model_module):
#      item = getattr(model_module, name)
#      if not isinstance(item, (type, types.ClassType)):
#        continue
#      # Found a model, bring into the module namespace.
#      exec "%s = item" % name
#      model_names.append(name)
# 
## Hide everything other than the classes from other modules.
#__all__ = model_names


#ORIGINAL CODE
PACKAGE = 'vt_manager.models'
MODEL_RE = r"^.*.py$"

# Search through every file inside this package.
model_names = []
model_dir = os.path.dirname( __file__)

for filename in os.listdir(model_dir):
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
    try:
	model_names.index(name)
    except Exception as e:
    	model_names.append(name)

# Hide everything other than the classes from other modules.
__all__ = model_names

