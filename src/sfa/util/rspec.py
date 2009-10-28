### $Id: rspec.py 14829 2009-08-19 19:35:01Z acb $
### $URL: http://svn.planet-lab.org/svn/sfa/trunk/sfa/util/rspec.py $

import sys
import pprint
import os
import httplib
from xml.dom import minidom
from types import StringTypes, ListType

class Rspec:

    def __init__(self, xml = None, xsd = None, NSURL = None):
        '''
        Class to manipulate RSpecs.  Reads and parses rspec xml into python dicts
        and reads python dicts and writes rspec xml

        self.xsd = # Schema.  Can be local or remote file.
        self.NSURL = # If schema is remote, Name Space URL to query (full path minus filename)
        self.rootNode = # root of the DOM
        self.dict = # dict of the RSpec.
        self.schemaDict = {} # dict of the Schema
        '''
 
        self.xsd = xsd
        self.rootNode = None
        self.dict = {}
        self.schemaDict = {}
        self.NSURL = NSURL 
        if xml: 
            if type(xml) == file:
                self.parseFile(xml)
            if type(xml) == str:
                self.parseString(xml)
            self.dict = self.toDict() 
        if xsd:
            self._parseXSD(self.NSURL + self.xsd)


    def _getText(self, nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc
  
    # The rspec is comprised of 2 parts, and 1 reference:
    # attributes/elements describe individual resources
    # complexTypes are used to describe a set of attributes/elements
    # complexTypes can include a reference to other complexTypes.
  
  
    def _getName(self, node):
        '''Gets name of node. If tag has no name, then return tag's localName'''
        name = None
        if not node.nodeName.startswith("#"):
            if node.localName:
                name = node.localName
            elif node.attributes.has_key("name"):
                name = node.attributes.get("name").value
        return name     
 
 
    # Attribute.  {name : nameofattribute, {items: values})
    def _attributeDict(self, attributeDom):
        '''Traverse single attribute node.  Create a dict {attributename : {name: value,}]}'''
        node = {} # parsed dict
        for attr in attributeDom.attributes.keys():
            node[attr] = attributeDom.attributes.get(attr).value
        return node
  
 
    def appendToDictOrCreate(self, dict, key, value):
        if (dict.has_key(key)):
            dict[key].append(value)
        else:
            dict[key]=[value]
        return dict

    def toGenDict(self, nodeDom=None, parentdict=None, siblingdict={}, parent=None):
        """
        convert an XML to a nested dict:
          * Non-terminal nodes (elements with string children and attributes) are simple dictionaries
          * Terminal nodes (the rest) are nested dictionaries
        """

        if (not nodeDom):
            nodeDom=self.rootNode

        curNodeName = nodeDom.localName

        if (nodeDom.hasChildNodes()):
            childdict={}
            for attribute in nodeDom.attributes.keys():
                childdict = self.appendToDictOrCreate(childdict, attribute, nodeDom.getAttribute(attribute))
            for child in nodeDom.childNodes[:-1]:
                if (child.nodeValue):
                    siblingdict = self.appendToDictOrCreate(siblingdict, curNodeName, child.nodeValue)
                else:
                    childdict = self.toGenDict(child, None, childdict, curNodeName)

            child = nodeDom.childNodes[-1]
            if (child.nodeValue):
                siblingdict = self.appendToDictOrCreate(siblingdict, curNodeName, child.nodeValue)
                if (childdict):
                    siblingdict = self.appendToDictOrCreate(siblingdict, curNodeName, childdict)
            else:
                siblingdict = self.toGenDict(child, siblingdict, childdict, curNodeName)
        else:
            childdict={}
            for attribute in nodeDom.attributes.keys():
                childdict = self.appendToDictOrCreate(childdict, attribute, nodeDom.getAttribute(attribute))

            self.appendToDictOrCreate(siblingdict, curNodeName, childdict)
            
        if (parentdict is not None):
            parentdict = self.appendToDictOrCreate(parentdict, parent, siblingdict)
            return parentdict
        else:
            return siblingdict



    def toDict(self, nodeDom = None):
        """
        convert this rspec to a dict and return it.
        """
        node = {}
        if not nodeDom:
             nodeDom = self.rootNode
  
        elementName = nodeDom.nodeName
        if elementName and not elementName.startswith("#"):
            # attributes have tags and values.  get {tag: value}, else {type: value}
            node[elementName] = self._attributeDict(nodeDom)
            # resolve the child nodes.
            if nodeDom.hasChildNodes():
                for child in nodeDom.childNodes:
                    childName = self._getName(child)
                    # skip null children 
                    if not childName:
                        continue
                    # initialize the possible array of children        
                    if not node[elementName].has_key(childName):
                        node[elementName][childName] = []
                    # if child node has text child nodes
                    # append the children to the array as strings
                    if child.hasChildNodes() and isinstance(child.childNodes[0], minidom.Text):
                        for nextchild in child.childNodes:
                            node[elementName][childName].append(nextchild.data)
                    # convert element child node to dict
                    else:       
                        childdict = self.toDict(child)
                        for value in childdict.values():
                            node[elementName][childName].append(value)
                    #node[childName].append(self.toDict(child))
        return node

  
    def toxml(self):
        """
        convert this rspec to an xml string and return it.
        """
        return self.rootNode.toxml()

  
    def toprettyxml(self):
        """
        print this rspec in xml in a pretty format.
        """
        return self.rootNode.toprettyxml()

  
    def parseFile(self, filename):
        """
        read a local xml file and store it as a dom object.
        """
        dom = minidom.parse(filename)
        self.rootNode = dom.childNodes[0]


    def parseString(self, xml):
        """
        read an xml string and store it as a dom object.
        """
        xml = xml.replace('\n', '').replace('\t', '').strip()
        dom = minidom.parseString(xml)
        self.rootNode = dom.childNodes[0]

 
    def _httpGetXSD(self, xsdURI):
        # split the URI into relevant parts
        host = xsdURI.split("/")[2]
        if xsdURI.startswith("https"):
            conn = httplib.HTTPSConnection(host,
                httplib.HTTPSConnection.default_port)
        elif xsdURI.startswith("http"):
            conn = httplib.HTTPConnection(host,
                httplib.HTTPConnection.default_port)
        conn.request("GET", xsdURI)
        # If we can't download the schema, raise an exception
        r1 = conn.getresponse()
        if r1.status != 200: 
            raise Exception
        return r1.read().replace('\n', '').replace('\t', '').strip() 


    def _parseXSD(self, xsdURI):
        """
        Download XSD from URL, or if file, read local xsd file and set schemaDict
        """
        # Since the schema definiton is a global namespace shared by and agreed upon by
        # others, this should probably be a URL.  Check for URL, download xsd, parse, or 
        # if local file, use local file.
        schemaDom = None
        if xsdURI.startswith("http"):
            try: 
                schemaDom = minidom.parseString(self._httpGetXSD(xsdURI))
            except Exception, e:
                # logging.debug("%s: web file not found" % xsdURI)
                # logging.debug("Using local file %s" % self.xsd")
                print e
                print "Can't find %s on the web. Continuing." % xsdURI
        if not schemaDom:
            if os.path.exists(xsdURI):
                # logging.debug("using local copy.")
                print "Using local %s" % xsdURI
                schemaDom = minidom.parse(xsdURI)
            else:
                raise Exception("Can't find xsd locally")
        self.schemaDict = self.toDict(schemaDom.childNodes[0])


    def dict2dom(self, rdict, include_doc = False):
        """
        convert a dict object into a dom object.
        """
     
        def elementNode(tagname, rd):
            element = minidom.Element(tagname)
            for key in rd.keys():
                if isinstance(rd[key], StringTypes) or isinstance(rd[key], int):
                    element.setAttribute(key, str(rd[key]))
                elif isinstance(rd[key], dict):
                    child = elementNode(key, rd[key])
                    element.appendChild(child)
                elif isinstance(rd[key], list):
                    for item in rd[key]:
                        if isinstance(item, dict):
                            child = elementNode(key, item)
                            element.appendChild(child)
                        elif isinstance(item, StringTypes) or isinstance(item, int):
                            child = minidom.Element(key)
                            text = minidom.Text()
                            text.data = item
                            child.appendChild(text)
                            element.appendChild(child) 
            return element
        
        # Minidom does not allow documents to have more then one
        # child, but elements may have many children. Because of
        # this, the document's root node will be the first key/value
        # pair in the dictionary.  
        node = elementNode(rdict.keys()[0], rdict.values()[0])
        if include_doc:
            rootNode = minidom.Document()
            rootNode.appendChild(node)
        else:
            rootNode = node
        return rootNode

 
    def parseDict(self, rdict, include_doc = True):
        """
        Convert a dictionary into a dom object and store it.
        """
        self.rootNode = self.dict2dom(rdict, include_doc).childNodes[0]
 
 
    def getDictsByTagName(self, tagname, dom = None):
        """
        Search the dom for all elements with the specified tagname
        and return them as a list of dicts
        """
        if not dom:
            dom = self.rootNode
        dicts = []
        doms = dom.getElementsByTagName(tagname)
        dictlist = [self.toDict(d) for d in doms]
        for item in dictlist:
            for value in item.values():
                dicts.append(value)
        return dicts

    def getDictByTagNameValue(self, tagname, value, dom = None):
        """
        Search the dom for the first element with the specified tagname
        and value and return it as a dict.
        """
        tempdict = {}
        if not dom:
            dom = self.rootNode
        dicts = self.getDictsByTagName(tagname, dom)
        
        for rdict in dicts:
            if rdict.has_key('name') and rdict['name'] in [value]:
                return rdict
              
        return tempdict


    def filter(self, tagname, attribute, blacklist = [], whitelist = [], dom = None):
        """
        Removes all elements where:
        1. tagname matches the element tag
        2. attribute matches the element attribte
        3. attribute value is in valuelist  
        """

        tempdict = {}
        if not dom:
            dom = self.rootNode
       
        if dom.localName in [tagname] and dom.attributes.has_key(attribute):
            if whitelist and dom.attributes.get(attribute).value not in whitelist:
                dom.parentNode.removeChild(dom)
            if blacklist and dom.attributes.get(attribute).value in blacklist:
                dom.parentNode.removeChild(dom)
           
        if dom.hasChildNodes():
            for child in dom.childNodes:
                self.filter(tagname, attribute, blacklist, whitelist, child) 


    def validateDicts(self):
        types = {
            'EInt' : int,
            'EString' : str,
            'EByteArray' : list,
            'EBoolean' : bool,
            'EFloat' : float,
            'EDate' : date}


    def pprint(self, r = None, depth = 0):
        """
        Pretty print the dict
        """
        line = ""
        if r == None: r = self.dict
        # Set the dept
        for tab in range(0,depth): line += "    "
        # check if it's nested
        if type(r) == dict:
            for i in r.keys():
                print line + "%s:" % i
                self.pprint(r[i], depth + 1)
        elif type(r) in (tuple, list):
            for j in r: self.pprint(j, depth + 1)
        # not nested so just print.
        else:
            print line + "%s" %  r
    


class RecordSpec(Rspec):

    root_tag = 'record'
    def parseDict(self, rdict, include_doc = False):
        """
        Convert a dictionary into a dom object and store it.
        """
        self.rootNode = self.dict2dom(rdict, include_doc)

    def dict2dom(self, rdict, include_doc = False):
        record_dict = rdict
        if not len(rdict.keys()) == 1:
            record_dict = {self.root_tag : rdict}
        return Rspec.dict2dom(self, record_dict, include_doc)

        
# vim:ts=4:expandtab
    
