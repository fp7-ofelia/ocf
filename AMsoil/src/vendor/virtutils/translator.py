import amsoil.core.log
import xmltodict
import json
#import uuid

logging=amsoil.core.log.getLogger('VTDelegate3')

class Translator:

    class Struct:
        """
        Allows to be filled with dictionary.
        """
        def __init__(self, **entries):
            self.__dict__.update(entries)
    
    @staticmethod
    def xml2json_from_file(file_path):
        return Translator.xml2json(open(file_path, "r"))
    
    @staticmethod
    def xml2json(xml_content):
        dictionary = xmltodict.parse(xml_content)
        json_content = json.loads(json.dumps(dictionary))
        return json_content
    
    @staticmethod
#    def dict2class(dictionary, container_class=Struct):
    def dict2class(dictionary, container_class=Struct):
        retrieved_class = container_class(**dictionary)
        return retrieved_class
    
    @staticmethod
#    def dict2existing_class(container_class, content_dict, slice_name, end_time):
    def dict2existing_class(container_class, content_dict):
#        logging.debug(">>> CURRENT CLASS: %s" % str(container_class.__dict__))
#        logging.debug(">>> CURRENT DICTIONARY: %s" % str(content_dict))
        retrieved_class = container_class(content_dict)
#        logging.debug(">>> DATA AFTER CONTAINER: %s" % str(retrieved_class.__dict__))
        return retrieved_class

#        container_class.name = content_dict['name']
#        container_class.memory = int(content_dict['memory_mb'])
#        container_class.hd_size_mb = float(content_dict['hd_size_mb'])/1024
#        container_class.project_name = content_dict['project_name']
#        container_class.slice_id = 0 #necessary?
#        container_class.slice_name = slice_name
#        container_class.operating_system_type = content_dict['operating_system_type']
#        container_class.operating_system_version = content_dict['operating_system_version']
#        container_class.operating_system_distribution = content_dict['operating_system_distribution']
#        container_class.hypervisor = content_dict['hypervisor']
#        container_class.hd_setup_type = content_dict['hd_setup_type']
#        container_class.hd_origin_path = content_dict['hd_origin_path']
#        container_class.virtualization_setup_type = content_dict['virtualization_setup_type']
#        container_class.server = VTServer.query.filter_by(name=content_dict['server_name']).one()
#        logging.debug("********************************* OK OK")
#        return container_class

