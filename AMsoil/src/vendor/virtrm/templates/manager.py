"""
Exposes the methods to access templates.
"""
from resources.vtserver import VTServer
from templates.template import Template
from utils.base import db
class TemplateManager():
    #
    # Direct operations over templates
    #
    def list_template_info(self, template_uuid):
        return db.session.query(Template).filter(uuid=template_uuid)
    
    def create_template(self, template_dictionary):
        db.session.query(Template).filter(uuid=template_uuid).constructor(template_dictionary)
    
    def edit_template(self, template_dictionary):
        if template_dictionary['uuid']:
            template = db.session.query(Template).filter(uuid=template_dictionary['uuid'])
        elif template_dictionary['name']:
            template = db.session.query(Template).filter(uuid=template_dictionary['name'])
        if len(template) != 1:
            raise Exception("Could not retrieve template to edit")
        for key in template_dictionary.keys():
            getattr(template, "set_%s" % key)(template_dictionary[key])
    
    def delete_template(self, template_uuid):
        db.session.query(Template).filter(uuid=template_uuid).delete()
    
    #
    # Operations over resources, related to templates
    #
    
    def add_template_to_server(self, server_uuid, template_uuid):
        db.session.query(Template).filter(uuid=template_uuid).add_to_server(VTServer.uuid=server_uuid)
    
    def delete_template_from_server(self, server_uuid, template_uuid):
        db.session.query(Template).filter(uuid=template_uuid).remove_from_server(VTServer.uuid=server_uuid)
    
    def copy_template_to_server(self, server_uuid, template_uuid):
        db.session.query(Template).filter(uuid=template_uuid).copy_to_server(VTServer.uuid=server_uuid)
    
    def move_template_to_server(self, server_uuid, template_uuid):
        self.copy_template_to_server(server_uuid, template_uuid)
        self.delete_template_from_server(server_uuid, template_uuid)
