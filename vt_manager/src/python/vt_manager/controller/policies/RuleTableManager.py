#from vt_manager.controller.policyEngine.RuleTable import RuleTable
from pypelib import RuleTable
from vt_manager.models import *
from ControllerMappings import *
from threading import Thread, Lock
#CBA
import uuid


'''
        @author: lbergesio, omoya

 
'''

class RuleTableManager():

	_instance = None
        _mutex = Lock()

        #Mappings contains the basic association between keywords and objects, functions or static values
        #Note that these mappings are ONLY defined by the lib user (programmer) 
        _ConditionMappings = ControllerMappings.getConditionMappings()

	_ActionMappings = {"None":"None",
			   "something":"None"}
	
	#Main methods 
	@staticmethod
	def setRuleTable(name,resolverMappings,defaultParser, defaultPersistance, defaultPersistanceFlag, pType, uuid):
		if CreatedRuledTables.objects.filter(name=name):
			print 'RuleTableManager(): if'
			return RuleTableManager.getRuleTable(name, resolverMappings)
		else:
			print 'RuleTableManager(): else'
			return RuleTableManager.createRuleTables(name,resolverMappings,defaultParser, defaultPersistance, defaultPersistanceFlag, pType,uuid)

	@staticmethod
        def load(name):
		if CreatedRuledTables.objects.filter(name=name):
			mapps = dict()
			mapps.update(RuleTableManager._ConditionMappings)
			mapps.update(RuleTableManager._ActionMappings)
			print mapps
                	return RuleTableManager.getRuleTable(name,mapps)
		else: 
			CreateModel = CreatedRuledTables(name = name, uuid = uuid.uuid4().hex)
                	CreateModel.save()
			return RuleTableManager.load(name)

	@staticmethod
	def getRuleTable(name, mapps):
	
		# If table does not exist, create it
		Table = RuleTable.loadOrGenerate(name, mapps, "RegexParser", "Django", True, True, uuid.uuid4().hex)
		return Table
	

	@staticmethod
	def createRuleTables(name,resolverMappings,defaultParser, defaultPersistance, defaultPersistanceFlag, pType,uuid):
		print 'creating...'	
		createdRuleTable = RuleTable(name,resolverMappings, defaultParser, defaultPersistance, defaultPersistanceFlag, pType, uuid)
		print 'saving...'
		#createdRuleTable.save()
		print createdRuleTable.name
		CreateModel = CreatedRuledTables(name = createdRuleTable.name, uuid = createdRuleTable.uuid)
		CreateModel.save()
		return createdRuleTable

	@staticmethod
	def evaluate(metaObj, RTname=None):
		if RTname == None:
			RTname = "RuleTable1"
		ruleTable = RuleTableManager.load(RTname)
		return ruleTable.evaluate(metaObj)

	#getters
	@staticmethod
	def getRuleSet(ruleTable):
                return ruleTable.getRuleSet()
	
	@staticmethod
        def getName(RuleTable):
                return ruleTable.getName()

	@staticmethod
        def getPolicyType(ruleTable):
                return ruleTable.getPolicyType()

	@staticmethod
        def getPersistence(ruleTable):
                return ruleTable.getPersistence()

	@staticmethod
        def getParser(ruleTable):
                return ruleTable.getParser

	@staticmethod
        def getResolverMappings(ruleTable):
                return ruleTable.getResolverMappings()

	@staticmethod
        def getPersistenceFlag(ruleTable):
                return ruleTable.getPersistenceFlag()
	

	#Useful Methods
	@staticmethod	
	def getRuleTableList():
		TableList = []
		Model = CreatedRuledTables.objects.all()
		for table in Model:
			TableList.append(table.name)
		return TableList	

	@staticmethod
	def loadUUID(name):
		if CreatedRuledTables.objects.filter(name=name):
			return str(CreatedRuledTables.objects.get(name=name).uuid)


	@staticmethod
	def getNameNUUID():
		TableList = list()
		Model = CreatedRuledTables.objects.all()
		for table in Model:
			dic = dict()
			dic = {'name':table.name,'uuid':table.uuid}
			TableList.append(dic)
		return TableList

	@staticmethod	
	def getRule(ruleTable,ruleID):

		for rule in ruleTable._ruleSet:
			print rule.rule._uuid, ruleID
			if str(rule.rule._uuid) == str(ruleID): 
				return rule.rule, ruleTable._ruleSet.index(rule),rule.enabled
		raise Exception("Cannot edit the rule")

	@staticmethod
	def getModelConditions(tableName):
		conditions = list()
		print tableName
		
		conditionModel =ConditionModel.objects.filter(ruletable = tableName)
		for cond in conditionModel:
			conditions.append(cond.condition)
			
		return conditions
	@staticmethod
	def saveCondition(string, table):
		conditionModel = ConditionModel(condition = string, ruletable = table)
		conditionModel.save()
		return

	@staticmethod
	def getPriorityList(ruleTable):
		mx = len(RuleTableManager.getRuleSet(ruleTable))
		i = 0
		out = []
		while i < mx:
			out.append(i)
			i += 1
		return out
			
	@staticmethod		
	def getConditionMappings():
		return RuleTableManager._ConditionMappings

	@staticmethod
	def getActionMappings():
		return RuleTableManager._ActionMappings
