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
    def dict2class(dictionary, container_class=Struct):
        retrieved_class = container_class(**dictionary)
        return retrieved_class
    
    @staticmethod
    def dict2existing_class(content_dict, container_class=None):
        if container_class:
            retrieved_class = container_class(content_dict, container_class)
        else:
            retrieved_class = dict2class(content_dict)
        return retrieved_class