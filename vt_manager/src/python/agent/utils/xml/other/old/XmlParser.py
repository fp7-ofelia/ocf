import sys 
import os
from xml import vtRspecInterface
'''
	@author: msune
	
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
	XML Parser class 
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
    XML Crafter class 
'''
class XmlCrafter(object):

    @staticmethod
    def craftXML(XMLclass):
        from StringIO import StringIO
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
