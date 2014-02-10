from utils.base import db
import amsoil.core.pluginmanager as pm

'''@author: msune, SergioVidiella'''


class ResourcesHash(db.Model):
    """Class to store resources hash"""

    config = pm.getService("config")
    __tablename__ = config.get("virtrm.DATABASE_PREFIX") + 'resourceshash'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    hash_value = db.Column("hashValue",db.String(1024), nullable=False)
    project_uuid = db.Column("projectUUID", db.String(1024), nullable=False)
    slice_uuid = db.Column("sliceUUID", db.String(1024), nullable=False)
