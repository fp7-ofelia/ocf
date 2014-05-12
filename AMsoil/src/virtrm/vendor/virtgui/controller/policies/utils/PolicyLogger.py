import logging
import os
from vt_manager.controller.policies.utils.PELogConf import *

'''
        @author: omoya
        @organization: i2CAT

        Simple Logger wrapper for VM Manager Policy Engine 
'''

class PolicyLogger():
        @staticmethod
        def getLogger():
                
		log = logging.getLogger('PolicyEngine')
		path = PolicyLogger.setUpConfiguration()
		formatter = logging.Formatter('[%(asctime)s] [%(filename)s] [%(funcName)s] [%(levelname)s]: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
		fileHandler = PolicyLogger.configureHandler(formatter,path)
                log.addHandler(fileHandler)
		return log

	@staticmethod
	def setUpConfiguration():
		path = os.path.dirname(os.path.abspath(__file__))
		
		open (path+"/log/pe.log","a+")
		return path+"/log/pe.log"


	@staticmethod 
	def configureHandler(formatter,path):
		#fileHandler = logging.FileHandler((PELogDir + "pe.log"))
		fileHandler = logging.FileHandler(path)
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

                fileHandler.setLevel(log_level)
                fileHandler.setFormatter(formatter)
		return fileHandler
