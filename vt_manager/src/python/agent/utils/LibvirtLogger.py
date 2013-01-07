import logging

'''
        @author: msune, omoya
        @organization: i2CAT, OFELIA FP7

        Simple Logger wrapper for Libvirt Event Monitoring 
'''
from utils.Logger import Logger

Libvirt = Logger.getLogger()

#Libvirt Monitoring Log File
LIBVIRT_LOG='/opt/ofelia/oxa/log/libvirtmonitor.log'


class LibvirtLogger():
        @staticmethod
        def getLogger():
                #Simple wrapper. Ensures logging is always correctly configured (logging.basicConfig is executed)
                return Libvirt.addHandler(logging.FileHandler(LIBVIRT_LOG))

