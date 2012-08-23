#!/usr/bin/python
import os
import sys
from os.path import dirname, join

PYTHON_DIR = os.getcwd()+'/../src/python/'
print PYTHON_DIR

# This is needed because wsgi disallows using stdout
sys.stdout = sys.stderr

os.environ['DJANGO_SETTINGS_MODULE'] = 'vt_manager.settings.settingsLoader'

sys.path.insert(0,PYTHON_DIR)

from vt_manager.controller.policies.RuleTableManager import RuleTableManager


#General Parametres
RuleTableName = None #leave it to None if you want to put the default rule/s into default rule table(provisioning)

#Custom Vars
NVMS = 10
RAM = 256

if not RuleTableMAnager.GetRuleSet(RuleTableName):
	if RuleTableManager.GetPolicyType(RuleTableName):
		operator = '>'
        	value = 'deny'
	else:
        	operator = '<='
        	value = 'accept'


	#Type default rules in rules tuple
	DEFAULT_RULES = (
		 'if ((number.vms %s %s) && (vm.memory_mb %s %s)) then %s  denyMessage You cannot request more than %s vms or %sMBytes/vm #Main Rule' %(operator,NVMS,operator,RAM,value,NVMS,RAM),

		)	

	for default_rule in DEFAULT_RULES:
		RuleTableManager.AddRule(default_rule,tableName=RuleTableName)

