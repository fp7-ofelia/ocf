import sys
sys.path.append("/opt/ofelia/AMsoil/src/virtrm/vendor/configdb/")
sys.path.append("/opt/ofelia/AMsoil/src/virtrm/")
sys.path.append("/opt/ofelia/AMsoil/src/virtrm/vendor/virtrm")
import amconfigdb
import amconfigdbexceptions
import amsoil.core.pluginmanager as pm
pm.registerService("testconfig", amconfigdb.ConfigDB())
pm.registerService("testconfigexceptions", amconfigdbexceptions)
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
import amsoil.core.pluginmanager as pm
from plugin import *

config = pm.getService("testconfig")
setup()
# Create  the Flask app
app = Flask(__name__)
# Add the database path
app.config['SQLALCHEMY_DATABASE_URI'] = "%s://%s:%s@%s/%s" % (
                                                config.get("virtrm.DATABASE_ENGINE"), config.get("virtrm.DATABASE_USER"),
                                                config.get("virtrm.DATABASE_PASSWORD"), config.get("virtrm.DATABASE_HOST"),
                                                config.get("virtrm.DATABASE_NAME"),
                                                )
# Create a new SQLAlchemy instance
db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

import os
import pkgutil
import models as package

for importer, modname, ispkg in pkgutil.walk_packages(path=package.__path__,
                                                       prefix=package.__name__+'.',
                                                       onerror=lambda x:None
                                                      ):
    if not ispkg:
        path = os.path.join(str(package.__path__[0]), "/".join(modname.split(".")[1:-1]))
        py_file = "%s.py" % str(modname.split(".")[-1])
        pyc_file = "%sc" % py_file
        # Try to remove .pyc files (to avoid left garbage)
        try:
            if os.path.isfile("%s/%s" % (str(path), pyc_file)):
                os.remove("%s/%s" % (path, pyc_file))
        # If no .pyc file found, do nothing
        except:
            pass
        # Try to import .py files (to load model)
        try:
            __import__(modname)
        # If no .py file found, do nothing
        except:
            pass

if __name__ == '__main__':
    manager.run()
