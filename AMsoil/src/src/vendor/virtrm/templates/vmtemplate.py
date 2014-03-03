from models.resources.virtualmachine import VirtualMachine
from templates.template import Template
from utils.base import db
import amsoil.core.pluginmanager as pm

'''@author: SergioVidiella'''

class VMTemplate(db.Model):
    """Relation between Servers and their supported Templates"""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'virtualmachine_template'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    virtualmachine_uuid = db.Column(db.Integer, db.ForeignKey(table_prefix + 'virtualmachine.uuid'), nullable=False)
    template_uuid = db.Column(db.Integer, db.ForeignKey(table_prefix + 'template.uuid'), nullable=False)

    template = db.relationship("Template", backref="virtualmachine_template")
    virtualmachine = db.relationship("VirtualMachine")

