from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import amsoil.core.pluginmanager as pm

config = pm.getService("config")
# Create a new SQLAlchemy instance
db = SQLAlchemy()
# Create  the Flask app
app = Flask(__name__)
# Add the database path
app.config['SQLALCHEMY_DATABASE_URI'] = "%s://%s:%s@%s/%s" % (
                                                config.get("virtrm.DATABASE_ENGINE"), config.get("virtrm.DATABASE_USER"),
                                                config.get("virtrm.DATABASE_PASSWORD"), config.get("virtrm.DATABASE_HOST"),
                                                config.get("virtrm.DATABASE_NAME"),
                                                )
db.init_app(app)

def set_up():
    with app.app_context():
        db.create_all()
