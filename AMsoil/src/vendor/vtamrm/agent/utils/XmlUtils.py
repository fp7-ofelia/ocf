import sys 
import os
from StringIO import StringIO
from xml import vtRspecInterface
from utils.Logger import Logger

'''
	@author: msune
	
	Parses the incoming XML to the object 
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

	logger = Logger.getLogger()	

	@staticmethod 
	def parseXML(rawXML):
		#XmlParser.logger.debug("Parsing XML...")
		try:			
			object = vtRspecInterface.parseString(rawXML)   	
			#XmlParser.logger.debug("Parsing of XML concluded without significant errors.")
			return object 
		except Exception as e:
            		XmlParser.logger.error(str(e)) 
			raise XMLParsingException("Could not parse parse XML;"+str(e))


'''
    XML Query Crafter class 
'''
class XmlCrafter(object):

	logger = Logger.getLogger()	
		
	@staticmethod
	def craftXML(XMLclass):
		#XmlCrafter.logger.debug("Crafting Model...")
        	try:
            		xml = StringIO()
           		xml.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            		#XMLclass.export(xml, level=0)
			XMLclass.export(xml, level=0,namespacedef_='xmlns=\"http://www.fp7-ofelia.eu/CF/vt_am/rspec\"')
            		#XmlCrafter.logger.debug("Crafting of the XML Class concluded without significant errors.")
            		xmlString = xml.getvalue()
            		xml.close()
            		return xmlString
        	except Exception as e:
            		XmlCrafter.logger.error(str(e)) 
            		raise XMLParsingException("Could not craft Model;"+str(e))
class XmlUtils(object):

	#TODO: improve this by creating a proper constructor	

	@staticmethod
	def getEmptyProvisioningResponseObject():
		with open(os.path.dirname(__file__)+'/xml/emptyProvisioningResponse.xml','r') as fxml:
			return XmlParser.parseXML(fxml.read())
		#return XmlParser.parseXML(open('utils/xml/emptyResponse.xml','r').read())

	@staticmethod
	def getEmptyMonitoringResponseObject():
		with open(os.path.dirname(__file__)+'/xml/emptyMonitoringResponse.xml','r') as fxml:
			return XmlParser.parseXML(fxml.read())
		#return XmlParser.parseXML(open('utils/xml/emptyResponse.xml','r').read())

	@staticmethod
	def getEmptyMonitoringVMsInfoResponseObject():
		with open(os.path.dirname(__file__)+'/xml/emptyMonitoringVMsInfoResponse.xml','r') as fxml:
			return XmlParser.parseXML(fxml.read())
		#return XmlParser.parseXML(open('utils/xml/emptyResponse.xml','r').read())


