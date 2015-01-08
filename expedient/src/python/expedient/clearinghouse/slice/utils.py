#def parseFVexception(exc):
#	try:
#	    return str(exc).split(':',2)[2][0:-2]
#        except:
#            return str(exc)
def parseFVexception(exc):
    import re
    try:
        # Parse a xmlrpclib.Fault error and retrieve its contents
        #r = [ re.findall("<(.*)>:(.*?): File (.*)\"", str(exc))[0][1] ]
        r = re.findall("[<(.*)>:]{0,1}(.*?):[ ]{0,}File (.*)", str(exc))[0]
    except Exception as e:
        try:
            r = re.findall("!!(.*?)!!", str(exc))
        except Exception as e:
            return str(exp)
    if r:
        return r[0]
    else:
        return str(exc)

class startAggregateException(Exception):
	def __init__(self, slice, agg):
		self.value = value
	def __str__(self):
		return repr("Could not start Aggregate Manager: %s in slice: %s."  %(agg.name, slice.name))
