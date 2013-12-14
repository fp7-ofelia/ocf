from base import db


'''@author: SergioVidiella'''


class ResourcesHash(db.Model):
    """Class to store resources hash"""

    __tablename__ = 'vt_manager_resourceshash'

    id = Column(db.Integer, autoincrement=True, primary_key=True)
    hash_value = db.Column("hashValue",db.String(1024), nullable=False)
    project_uuid = db.Column("projectUUID", db.String(1024), nullable=False)
    slice_uuid = db.Column("slice_uuid", db.String(1024), nullable=False)
