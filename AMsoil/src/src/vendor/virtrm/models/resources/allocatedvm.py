from models.resources.virtualmachine import VirtualMachine
from models.resources.vtserver import VTServer
from utils.base import db
import amsoil.core.log
import amsoil.core.pluginmanager as pm
import uuid

logging=amsoil.core.log.getLogger('AllocatedVM')

'''@author: SergioVidiella'''

class AllocatedVM(VirtualMachine):
    """Virtual Machines allocated for GeniV3 calls."""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'allocatedvm'
    __table_args__ = {'extend_existing':True}

    '''General parameters'''
    virtualmachine_ptr_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'virtualmachine.id'), primary_key=True)
    server_uuid = db.Column(db.ForeignKey(table_prefix + 'vtserver.uuid'), nullable=False) 

    server = db.relationship("VTServer", uselist=False, backref=db.backref("allocated_vms"))
    vm = db.relationship("VirtualMachine", uselist=False, backref=db.backref("allocatedvm", cascade = "all, delete-orphan"))
    

    @staticmethod
    def __init__(self, **params_dict):
        logging.debug("......... self.__dict__ = %s" % str(self.__table__.columns))
        logging.debug("......... params_dict = %s" % str(params_dict))
        # Looks for common attributes between the class' inner dictionary and the one passed through arguments
#        common_attributes = set(params_dict.keys()) & set(self.__dict__.keys())
        # Remove prefix with the name of the table
        class_data = dir(self)
#        table_columns = self.__table__.columns._data.keys()
        logging.debug("......... class attributes = %s" % str(class_data))
#        table_foreign_keys = [ str(key._get_colspec()) for key in self.__table__.foreign_keys ]
        common_attributes = set(params_dict.keys()) & set(class_data)
#        common_attributes = set(params_dict.keys()) & (set(table_columns) | set(table_foreign_keys))
        logging.debug("......... common attributes = %s" % str(common_attributes))
        common_dictionary = dict()
        for attribute in common_attributes:
            logging.debug("******** ALLOCATING %s => VALUE %s" % (attribute, params_dict[attribute]))
            common_dictionary[attribute] = params_dict[attribute]
        # Then updates the class' inner dictionary with the one retrieved after the intersection of their keys
        try:
            self.__dict__.update(**common_dictionary)
        except Exception as e:
            raise e
#        try:
            # XXX COULD NOT AUTOMATE IT WITH THE FOREIGN KEYS FROM THE MODEL
#            self.server = params_dict["server"]
#        except Exception as e:
#            raise e
        # Set the state to allocated
        try:
            common_dictionary.pop("state")
        except:
            pass
        self.state = VirtualMachine.ALLOCATED_STATE
        # If 'do_save' does not exist, set to False
        try:
            common_dictionary["do_save"]
        except:
            self.do_save = False
        self.auto_save()
