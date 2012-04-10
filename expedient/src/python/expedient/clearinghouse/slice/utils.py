def parseFVexception(exc):
	try:
	    return str(exc).split(':',2)[2][0:-2]
        except:
            return str(exc)
