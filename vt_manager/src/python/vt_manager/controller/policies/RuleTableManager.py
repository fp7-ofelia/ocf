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

	_tableName = 'RuleTable1'

        #Mappings contains the basic association between keywords and objects, functions or static values
        #Note that these mappings are ONLY defined by the lib user (programmer) 
        _ConditionMappings = ControllerMappings.getConditionMappings()

	_ActionMappings = {"None":"None",
			   "something":"None"}
	
	#Main methods 
	@staticmethod
	def setRuleTable(name,resolverMappings,defaultParser, defaultPersistance, defaultPersistanceFlag, pType, uuid):
		if CreatedRuledTables.objects.filter(name=name):
			return RuleTableManager.getRuleTable(name, resolverMappings)
		else:
			return RuleTableManager.createRuleTables(name,resolverMappings,defaultParser, defaultPersistance, defaultPersistanceFlag, pType,uuid)

	@staticmethod
        def load(name = None):
		if not name:
			name = RuleTableManager._tableName
		if CreatedRuledTables.objects.filter(name=name):
			mapps = dict()
			mapps.update(RuleTableManager._ConditionMappings)
			mapps.update(RuleTableManager._ActionMappings)
                	return RuleTableManager.getRuleTable(name,mapps)
		else: 
			CreateModel = CreatedRuledTables(name = name, uuid = uuid.uuid4().hex)
                	CreateModel.save()
			return RuleTableManager.load(name)
	@staticmethod
	def getRuleTable(name, mapps):
		with RuleTableManager._mutex:
			if not RuleTableManager._instance:
				# If table does not exist, create it
				 RuleTable.loadOrGenerate(name, mapps, "RegexParser", "Django", True, True, uuid.uuid4().hex)
		return RuleTable._instance

	@staticmethod
	def createRuleTables(name,resolverMappings,defaultParser, defaultPersistance, defaultPersistanceFlag, pType,uuid):
		createdRuleTable = RuleTable(name,resolverMappings, defaultParser, defaultPersistance, defaultPersistanceFlag, pType, uuid)
		CreateModel = CreatedRuledTables(name = createdRuleTable.name, uuid = createdRuleTable.uuid)
		CreateModel.save()
		return createdRuleTable

	@staticmethod
	def evaluate(metaObj, RTname=None):
		if RTname == None:
			RTname = RuleTableManager._tableName
		ruleTable = RuleTableManager.load(RTname)
		return ruleTable.evaluate(metaObj)

	#getters
	@staticmethod
	def getRuleSet(name = None):
                return RuleTableManage.load().getRuleSet()
	
	@staticmethod
        def getName(name = None):
                return RuleTableManager.load().getName()

	@staticmethod
        def getPolicyType(name = None):
                return RuleTableManager.load().getPolicyType()

	@staticmethod
        def getPersistence(name = None):
                return RuleTableManager.load().getPersistence()

	@staticmethod
        def getParser(name = None):
                return RuleTableManager.load().getParser()

	@staticmethod
        def getResolverMappings(name = None):
                return RuleTableManager.load().getResolverMappings()

	@staticmethod
        def getPersistenceFlag(name = None):
                return RuleTableMAnager.load().getPersistenceFlag()

	#Useful Methods
	@staticmethod	
	def getRuleTableList(name = None):
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
	def getRule(ruleID,name=None):
		ruleTable = RuleTable.load(name)
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
	def getPriorityList(name = None):
		RuleTable = RuleTableManager.load(name)
		mx = len(RuleTableManager._ruleSet)
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

	
	def getDefaultName(self):
		return self._tableName
