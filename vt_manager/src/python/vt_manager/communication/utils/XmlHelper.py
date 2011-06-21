from vt_manager.controller import *
import sys
import os
from StringIO import StringIO
from agent.utils.xml import vtRspecInterface
'''
    @author: msune, lber
    
    Parses the incoming XML to the data model
'''

'''
    Parsing Exception 
'''
class XMLParsingException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


'''
    XML Query Parser class 
'''
class XmlParser(object):

    @staticmethod
    def parseXML(rawXML):
        print "Parsing XML..."
        try:
            object = vtRspecInterface.parseString(rawXML)
            print "Parsing of XML concluded without significant errors."
            return object
        except Exception as e:
            #TODO: add more info
            print >> sys.stderr, e
            raise XMLParsingException("Could not parse parse XML; traceback\n")


'''
    XML Query Crafter class 
'''
class XmlCrafter(object):

    @staticmethod
    def craftXML(XMLclass):
        print "Crafting Model..."
        try:
            xml = StringIO()
            xml.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            XMLclass.export(xml, level=0)
            print "Crafting of the XML Class concluded without significant errors."
            xmlString = xml.getvalue()
            xml.close()
            return xmlString
        except Exception as e:
            #TODO: add more info
            print >> sys.stderr, e
            raise XMLParsingException("Could not craft Model; traceback\n")

def xmlFileToString(file):
    try:        
        f = open(file, 'r')
        xml =  f.read()
        #print xml
        return xml
    except Exception:
        print "Oops!  File not found"


class XmlHelper(object):

    #TODO: improve this by creating a proper constructor    

    @staticmethod
    def getSimpleActionSpecificQuery(type, serverUUID):
        
         simpleRspec =  XmlHelper.parseXmlString(open(os.path.dirname(__file__)+'/xml/queryProvisioning.xml','r').read())
         if type == 'stop': type = 'hardStop'
         simpleRspec.query.provisioning.action[0].type_ = type
         simpleRspec.query.provisioning.action[0].server.uuid = serverUUID
         return simpleRspec
#        if type == 'start':
#            simpleRspec =  XmlHelper.parseXmlString(open(os.path.dirname(__file__)+'/xml/queryStart.xml','r').read())
#        if type == 'delete':
#            simpleRspec =  XmlHelper.parseXmlString(open(os.path.dirname(__file__)+'/xml/queryDelete.xml','r').read())            
#        if type == 'stop':
#            simpleRspec =  XmlHelper.parseXmlString(open(os.path.dirname(__file__)+'/xml/queryStop.xml','r').read())
#        if type == 'reboot':
#            simpleRspec =  XmlHelper.parseXmlString(open(os.path.dirname(__file__)+'/xml/queryReboot.xml','r').read())
#        return simpleRspec

    @staticmethod
    def getProcessingResponse(status, action,  description, ):
        simpleRspec =  XmlHelper.parseXmlString(open(os.path.dirname(__file__)+'/xml/emptyResponse.xml','r').read())
        simpleRspec.response.provisioning.action[0].status = status
        simpleRspec.response.provisioning.action[0].description = description
        #XXX:This is because the ActionController sends a dummy, None, dummy request
        if action != None: 
            simpleRspec.response.provisioning.action[0].id = action.id
            simpleRspec.response.provisioning.action[0].server.uuid = action.server.uuid
        return simpleRspec

    @staticmethod
    def getSimpleActionQuery(action=None):
        simpleRspec =  XmlHelper.parseXmlString(open(os.path.dirname(__file__)+'/xml/simpleActionQuery.xml','r').read())
        if action:
            simpleRspec.query.provisioning.action[0] = action
        return simpleRspec

    @staticmethod
    def getSimpleInformation():
        simpleRspec =  XmlHelper.parseXmlString(open(os.path.dirname(__file__)+'/xml/simpleListResources.xml','r').read())
        return simpleRspec

    @staticmethod
    def getListActiveVMsQuery():
        simpleRspec =  XmlHelper.parseXmlString(open(os.path.dirname(__file__)+'/xml/listActiveVMsQuery.xml','r').read())
        return simpleRspec



    @staticmethod
    def craftSimpleActionQuery(SimpleRspec, status, description):
        SimpleRspec.query.provisioning.action[0].status = status
        SimpleRspec.query.provisioning.action[0].description = description
        return craiftXmlClass(SimpleRspec)

    @staticmethod
    def parseXmlString(xml):
        return XmlParser.parseXML(xml)

    #def parseXmlStringResponse(xml):
    #    return XmlResponseParser.parseXML(xml)

    @staticmethod
    def craftXmlClass(xmlClass):
        return XmlCrafter.craftXML(xmlClass)
