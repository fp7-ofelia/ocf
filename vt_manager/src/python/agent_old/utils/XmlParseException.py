'''
	@author: msune
	
	Parses the incoming XML to the data model
'''
class MyError(Exception):
    	def __init__(self, value):
        	self.value = value
	def __str__(self):
	return repr(self.value)


