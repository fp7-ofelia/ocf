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
    import_models()
    with app.app_context():
        db.create_all()

def import_models():
    import pkgutil
    import models as package

    for importer, modname, ispkg in pkgutil.walk_packages(path=package.__path__, 
                                                          prefix=package.__name__+'.', 
                                                          onerror=lambda x:None
                                                         ):
        if not ispkg:
            __import__(modname)
            logging.debug("************** imported **************" + modname)
