"""
Parsing tests.

@date: Jun 12, 2013
@author: CarolinaFernandez
"""

# ----- Parse resources (lxml) -----
from lxml import etree

context = etree.iterparse("resources.xml")
for action, elem in context:
    if elem.tag == "resource":
        print ""
    if elem.text.strip():
        print("[%s] %s: %s" % (action, elem.tag, elem.text))

# ----- Add resources (lxml) -----
parser = etree.XMLParser(remove_blank_text=True)
tree = etree.parse("resources.xml", parser)
resources = tree.getroot()

new_resource = etree.SubElement(resources, "resource")
new_resource_name = etree.SubElement(new_resource, "name")
new_resource_name.text = "Sensor6"
new_resource_temperature = etree.SubElement(new_resource, "temperature")
new_resource_temperature.text = "21"
new_resource_temperature_scale = etree.SubElement(new_resource, "temperature_scale")
new_resource_temperature_scale.text = "K"

#print "Final XML: %s" % str(etree.tostring(tree, pretty_print=True))
# Formats output XML
tree.write ("resources.xml", pretty_print=True)


## ----- Parse resources (minidom) -----
#from xml.dom import minidom
#
#def getText(nodelist):
#    rc = []
#    for node in nodelist:
#        if node.nodeType == node.TEXT_NODE:
#            rc.append(node.data)
#    return ''.join(rc)
#
#xmldoc = minidom.parse("resources.xml")
#resource_list = xmldoc.getElementsByTagName("resource") 
#print len(resource_list)
#print ""
#
#for resource in resource_list:
#    name = resource.getElementsByTagName("name")[0]
#    temperature = resource.getElementsByTagName("temperature")[0]
#    temperature_scale = resource.getElementsByTagName("temperature_scale")[0]
#    interface_list = resource.getElementsByTagName("interface")
#    for interface in interface_list:
#        print "interface: %s" % getText(interface.childNodes)
#
## ----- Add resources (minidom) -----
#
#resource = xmldoc.createElement("resource")
#resource_text = xmldoc.createTextNode("name")
#resource.appendChild(resource_text)
#print "resource: %s" % str(resource.toxml())
##print "child nodes: %s" % str(xmldoc.childNodes[0].toxml())
#xmldoc.childNodes[0].appendChild(resource)
#print xmldoc.toxml()

