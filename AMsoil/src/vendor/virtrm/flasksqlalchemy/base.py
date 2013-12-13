from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


#config = pm.getService("config")
app = Flask(__name__)
#XXX: Get it from settings
app.config['SQLALCHEMY_DATABASE_URI'] = "%s://%s:%s@%s/%s" % ("mysql", "root", "ofelia4you", "localhost", "vt_am879544567")
db = SQLAlchemy(app)
