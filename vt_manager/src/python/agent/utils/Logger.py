import logging
import threading 

'''
        @author: msune
        @organization: i2CAT, OFELIA FP7

       	Simple Logger wrapper 
'''

#Get log level
from settings.settingsLoader import LOG_LEVEL 

#Configure logger
log_level= ""
if LOG_LEVEL == "INFO":
	log_level = logging.INFO
elif LOG_LEVEL == "WARNING":
	log_level = logging.WARNING
elif LOG_LEVEL == "ERROR":
	log_level = logging.ERROR
elif LOG_LEVEL == "CRITICAL":
	log_level = logging.CRITICAL
else:
	log_level = logging.DEBUG

threadId="main"
try:
	threadId = threading.current_thread().OXAId
except:
	pass

logging.basicConfig(format='%(asctime)s [%(threadName)s>%(filename)s:%(lineno)d] %(levelname)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', level=log_level)

class Logger():
	@staticmethod
	def getLogger():
		#Simple wrapper. Ensures logging is always correctly configured (logging.basicConfig is executed)
		return logging.getLogger()
