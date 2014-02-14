from models.resources.vmallocated import VMAllocated
from templates.template import Template
from utils.base import db
import amsoil.core.pluginmanager as pm

'''@author: SergioVidiella'''

class VMAllocatedTemplate(db.Model):
    """Relation between Servers and their supported Templates"""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'virtualmachine_allocated_template'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    virtualmachine_allocated_uuid = db.Column(db.Integer, db.ForeignKey(table_prefix + 'virtualmachine_allocated.uuid'), nullable=False)
    template_uuid = db.Column(db.Integer, db.ForeignKey(table_prefix + 'template.uuid'), nullable=False)

    template = db.relationship("Template", backref="vmallocated_template")
    vmallocated = db.relationship("VMAllocated")
