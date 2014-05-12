"""
Exposes the methods to access templates.
"""
from templates.template import Template
from utils.base import db
class TemplateManager():

    def __init__(self, templates=list(), save=False):
        self.template_buffer = templates
        self.persist = save

    def add_to_buffer(self, template):
        self.template_buffer.append(template)
    
    def remove_from_buffer(self, template):
        self.template_buffer.remove(template)     

    def add_template(self, template):
        if not isinstance(template, Template):
            raise TypeError("Template Manager Error: 'add_template' only accepts Template instances as argument")
        self.add_to_buffer(template)

    def create_template(self, name="",description="",os_type="",os_version="",os_distro="",virt_type="",hd_setup_type="",hd_path="",extended_data=None,img_url="",virt_tech="", save=False):
        template =Template(name,description,os_type,os_version,os_distro,virt_type,hd_setup_type,hd_path,extended_data,img_url,virt_tech,False)
        self.add_to_buffer(template)

    def get_template_by(self, my_filter=dict()):
#        return db.session.query(Template).filter_by(**my_filter)
        # XXX: Return Hardcoded information
        from templates_hardcoded_info import TEMPLATE
        return TEMPLATE

    def edit_template(self, new_attrs,template=None, my_filter=dict()):
        if not template:
            template = self.get_template_by(my_filter)
        if template in self.template_buffer:
            self.remove_from_buffer(template)
        for attr in new_attrs.keys():
            setattr(template, attr, new_attrs[attr])
        self.add_to_buffer(template)    

    def remove_template(self, template=None, my_filter=dict()):
        if not template:
            template = self.get_template_by(my_filter)
        if template in self.template_buffer:
            self.remove_from_buffer(template)
        try:
            template.delete()
        except:
            pass

    def add_template_to_server(self, server_uuid, template_uuid):
        #db.session.query(Template).filter(uuid=template_uuid).add_to_server(VTServer.uuid=server_uuid)
        pass

    def delete_template_from_server(self, server_uuid, template_uuid):
        #db.session.query(Template).filter(uuid=template_uuid).remove_from_server(VTServer.uuid=server_uuid)
        pass

    def copy_template_to_server(self, server_uuid, template_uuid):
        #db.session.query(Template).filter(uuid=template_uuid).copy_to_server(VTServer.uuid=server_uuid)
        pass

    def move_template_to_server(self, server_uuid, template_uuid):
        #self.copy_template_to_server(server_uuid, template_uuid)
        #self.delete_template_from_server(server_uuid, template_uuid)
        pass

    def add_template_to_vm(self, vm_uuid, template):
        pass

    def upadte_template_from_vm(self, vm_uuid):
        pass

    def get_templates_from_server(self, server_uuid):
        from templates_hardcoded_info import TEMPLATE
        return [TEMPLATE]

    def get_template_from_vm(self, vm_uuid):
        from templates_hardcoded_info import TEMPLATE
        return TEMPLATE
