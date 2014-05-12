'''
Created on Jul 10, 2012

@author: jnaous, CarolinaFernandez, SergioVidiella
'''

import re

ASCII_RE = "^([0-9a-zA-Z\-\_\ ])+$";
DATAPATH_RE = "^([0-9a-fA-F]{2}[:-]){7}([0-9a-fA-F]{2})$";
MAC_RE = "^([\dA-Fa-f]{2}:){5}[\dA-Fa-f]{2}$";
NOTBLANK_RE = "^.+$";
NUMBER_RE = "^([0-9])+$";
RESOURCE_RE = "^([0-9a-zA-Z\-\_])+$";
RESOURCE_VM_RE = "^([0-9a-zA-Z\-]){1,64}$";
TEXT_RE = "^([0-9a-zA-Z\-\_\ \.])+$";


def ascii_validator(s):
    pattern = re.compile(ASCII_RE)
    if (pattern.match(s) == None):
        raise Exception("Please do not use accented characters and avoid using \'@\'.")

def check_blank(value):
    if value=='': 
	raise Exception("Field required")

def datapath_validator(s):
    pattern = re.compile(DATAPATH_RE)
    if (pattern.match(s) == None):
	raise Exception("Please provide a valid datapath ID.")

def mac_validator(s):
    pattern = re.compile(MAC_RE)
    if (pattern.match(s) == None):
	raise Exception("Please provide a valid MAC address.")

def number_validator(s):
    pattern = re.compile(NUMBER_RE)
    if (pattern.match(str(s)) == None):
	raise Exception("Please use numbers only.")

def resource_name_validator(s):
    pattern = re.compile(RESOURCE_RE)
    if (pattern.match(s) == None):
	raise Exception("Please do not use accented characters, symbols or whitespaces.")

def vm_name_validator(s):
    pattern = re.compile(RESOURCE_VM_RE)
    if (pattern.match(s) == None):
	raise Exception("Please do not use accented characters, symbols, underlines or whitespaces.")
