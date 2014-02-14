import xmltodict
import json
import uuid

class Translator:

    @staticmethod
    def xml2json_from_file(file_path):
        return Translator.xml2json(open(file_path, "r"))
    
    @staticmethod
    def xml2json(xml_content):
        dictionary = xmltodict.parse(xml_content)
        json_content = json.loads(json.dumps(dictionary))
        return json_content
