from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


config = pm.getService("config")
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "%s://%s:%s@%s/%s" % (
                                                                config.get("virtrm.DATABASE_ENGINE"), config.get("virtrm.DATABASE_USER"),
                                                                config.get("virtrm.DATABASE_PASSWORD"), config.get("virtrm.DATABASE_HOST"),
                                                                config.get("virtrm.DATABASE_NAME"),
                                                                )
db = SQLAlchemy(app)
