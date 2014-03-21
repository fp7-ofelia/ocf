from models.resources.virtualmachine import VirtualMachine
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
    virtualization_technology = db.Column(db.String(1024), nullable=False, default="")
    vm = db.relationship("VirtualMachine", backref=db.backref("allocatedvm", cascade = "all, delete-orphan")))

    @staticmethod
#    def __init__(self,name="",project_id="",slice_id="",slice_name="",project_name="",server=None,memory=0,disc_space_gb=None,number_of_cpus=None,virt_tech="xen",expires=None,save=False):
    def __init__(self, **params_dict):
#        logging.debug("......... self.__dict__ = %s" % str(self.__dict__))
        logging.debug("......... self.__dict__ = %s" % str(self.__table__.columns))
        logging.debug("......... params_dict = %s" % str(params_dict))
        # Looks for common attributes between the class' inner dictionary and the one passed through arguments
#        common_attributes = set(params_dict.keys()) & set(self.__dict__.keys())
        # Remove prefix with the name of the table
        table_columns = self.__table__.columns._data.keys()
        logging.debug("......... table = %s" % str(self.__table__.__dict__))
        logging.debug("......... columns = %s" % str(table_columns))
        logging.debug("......... foreign keys 1 = %s" % str(self.__table__.foreign_keys))
        table_foreign_keys = [ (key.name, str(key)) for key in self.__table__.foreign_keys ]
        logging.debug("......... foreign keys 1+ = %s" % str(table_foreign_keys))
        table_foreign_keys = [ str(key._get_colspec()) for key in self.__table__.foreign_keys ]
        logging.debug("......... foreign keys 2 = %s" % str(table_foreign_keys))
        common_attributes = set(params_dict.keys()) & (set(table_columns) | set(table_foreign_keys))
        logging.debug("......... common attributes = %s" % str(common_attributes))
        common_dictionary = dict()
        for attribute in common_attributes:
            common_dictionary[attribute] = params_dict[attribute]
        # Then updates the class' inner dictionary with the one retrieved after the intersection of their keys
        self.__dict__.update(**common_dictionary)
        try:
            # XXX COULD NOT AUTOMATE IT WITH THE FOREIGN KEYS FROM THE MODEL
            self.server = params_dict["server"]
        except:
            pass
        # If UUID is not given, generate it
        try:
            common_dictionary["uuid"]
        except:
            self.uuid = uuid.uuid4()
        # If 'do_save' does not exist, set to False
        try:
            common_dictionary["do_save"]
        except:
            self.do_save = False
        if self.do_save:
            db.session.add(self)
            db.session.commit()
    
    def auto_save(self):
        if self.do_save is True:
            self.save()
  
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    '''Destructor'''
    @db.validates('virtualization_technology')
    def validate_virtualization_technology(self, key, virt_tech):
        try:
            VirtTechClass.validate_virt_tech(virt_tech)
            return virt_tech
        except Exception as e:
            raise e        
    
    '''Getters and Setters'''
    def set_virtualization_technology(self, virt_tech):
        self.virtualization_technology = virt_tech
        self.auto_save()
    
    def get_virtualization_technology(self):
        return self.virtualization_technology
