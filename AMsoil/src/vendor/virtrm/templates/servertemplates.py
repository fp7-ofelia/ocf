from resources.vtserver import VTServer
from templates.template import Template
from utils.base import db
import amsoil.core.pluginmanager as pm

'''@author: SergioVidiella'''

class ServerTemplates(db.Model):
    """Relation between Servers and their supported Templates"""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'vtserver_templates'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    vtserver_uuid = db.Column(db.Integer, db.ForeignKey(table_prefix + 'vtserver.uuid'), nullable=False)
    template_uuid = db.Column(db.Integer, db.ForeignKey(table_prefix + 'template.uuid'), nullable=False)

    template = db.relationship("Template", backref="vtserver_templates")
    vtserver = db.relationship("VTServer")
