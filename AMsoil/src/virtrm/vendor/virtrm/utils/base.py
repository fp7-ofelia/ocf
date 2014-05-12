from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import amsoil.core.log
import amsoil.core.pluginmanager as pm

logging=amsoil.core.log.getLogger('Base')

config = pm.getService("config")
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

def set_up():
    create_db()
    load_models()

def create_db():
    import os
    # Prepare database creation command
    command_db_creation = "mysql -u %s -p%s --execute=\"CREATE DATABASE IF NOT EXISTS %s;\"" % (config.get("virtrm.DATABASE_USER"), config.get("virtrm.DATABASE_PASSWORD"), config.get("virtrm.DATABASE_NAME"))
    if not config.get("virtrm.DATABASE_PASSWORD"):
        command_db_creation = "mysql -u %s --execute=\"CREATE DATABASE IF NOT EXISTS %s;\"" % (config.get("virtrm.DATABASE_USER"), config.get("virtrm.DATABASE_NAME"))
    # Perform operation
    try:
        db_error = os.system(command_db_creation)
    except:
        pass

def load_models():
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
            # For every model imported, generate the database table
            with app.app_context():
                db.create_all()
            logging.debug("************** imported **************" + modname)

def drop_table():
    with app.app_context():
        db.drop_all()
