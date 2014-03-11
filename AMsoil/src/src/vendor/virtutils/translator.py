import amsoil.core.log
import lxml
import xmltodict
import json

logging=amsoil.core.log.getLogger('VirtUtils')

"""
        @author: CarolinaFernandez, SergioVidiella

        General {translator, encoder/decoder} to/from JSON, XML, etc.
"""

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
    
    # XXX: Legacy. Manual version. Thought it was a nice code, though.
    def json2xml_manual(dictionary, xml_content="", level=0):
        """
        Encodes JSON content into an XML.
        Format set by adding manual indentations over recursions.
        """
        for key in dictionary.keys():
            indentation = level * "  "
            start_tag = "\n%s<%s>" % (indentation, str(key))
            end_tag = "</%s>" % str(key)
            xml_content += start_tag
            if type(dictionary[key]) is dict:
                # Increase indentation level for subdictionaries
                level += 1
                # And reduce for its corresponding ending tag
                return "%s\n%s%s" % (json2xml_content(dictionary[key], xml_content,level), (level-1) * "  ", end_tag)
            else:
                xml_content += str(dictionary[key])
            xml_content += end_tag
        return xml_content
    
    @staticmethod
    def json2xml(dictionary, xml_content="", namespace=""):
        """
        Encodes JSON content into an XML.
        Allows to define a namespace when needed.
        TODO: parse tags set by 'xmltodict'.
        """
        for key in dictionary.keys():
            start_tag = "<%s%s%s>" % (namespace, (":" if namespace else ""), key)
            end_tag = "</%s%s%s>" % (namespace, (":" if namespace else ""), key)
            xml_content += start_tag
            if type(dictionary[key]) is dict:
                return "%s%s" % (json2xml_content(dictionary[key], xml_content, namespace), end_tag)
            else:
                xml_content += str(dictionary[key])
            xml_content += end_tag
        return xml_content
    
    @staticmethod
    def json2lxml_tree(dictionary, xml_content=""):
        """
        Encodes JSON content into an XML.
        Format set by using 'lxml' library.
        """
        xml_content = Translator.json2xml(dictionary)
        # Helps when encoding XML with namespace defined
        parser = lxml.etree.XMLParser(recover=True)
        xml_tree = lxml.etree.fromstring(xml_content, parser)
        xml_tree_string = lxml.etree.tostring(xml_tree, pretty_print=True)
        return xml_tree_string

    @staticmethod
    def dict2xml_tree(dictionary, root_node, node_generator):
        """
        FIXME: try to make this more generic by NOT using 'node_generator'
        and ideally 'root_node'.
        @root_node: initial LXML tree with namespace definition, etc.
        @node_generator: LXML node that helps appending other nodes.
        """
        for key in dictionary.keys():
            if type(dictionary[key]) is list:
                node = getattr(node_generator, key)()
                for internal_dict in dictionary[key]:
                    int_node = getattr(node_generator, key[:-1])()
                    internal_node = Translator.dict2xml_tree(internal_dict, int_node, node_generator)
                    node.append(int_node)
            elif type(dictionary[key]) is dict:
                node = getattr(node_generator, key)()
                internal_node = Translator.dict2xml_tree(dictionary[key], node, node_generator)
                node.append(internal_node)
            else:
                node = getattr(node_generator, key)(str(dictionary[key]))
            root_node.append(node)
        return root_node
    
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

    @staticmethod
    def class2dict(content_class):
        return dict((key, value) for key, value in content_class.__dict__.iteritems() if not callable(value) and not key.startswith('_'))

    @staticmethod
    def model2dict(content_model):
        import sqlalchemy
        dictionary = Translator.class2dict(content_model)
        for key in dir(content_model):
            logging.debug("************* Model %s => Attribute %s" % (str(content_model), key))
            model_attr = getattr(content_model, key)
            logging.debug("************* Attribute => %s" % str(model_attr))
            if type(model_attr) is sqlalchemy.ext.associationproxy._AssociationList and model_attr: 
                logging.debug("************ Association key %s :Object %s" % (key, str(model_attr)))
                dictionary[key] = list()
                for attr in model_attr:
                    internal_model = Translator.class2dict(attr)
                    dictionary[key].append(internal_model)
        return dictionary
               
