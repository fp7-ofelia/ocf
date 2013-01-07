from pypelib.RuleTable import RuleTable
from pypelib.utils.Exceptions import *
from ControllerMappings import ControllerMappings
from threading import Thread, Lock
from utils.PolicyLogger import PolicyLogger
from django.conf import settings
from django.core.mail import send_mail
#CBA
import uuid


'''
        @author: lbergesio, omoya, CarolinaFernandez
 
'''

RAM = 512
NVMS = 10

class RuleTableManager():

	#RuleTableManager atributes
	_instance = None
        _mutex = Lock()
	_createdRuleTables = list()
	logger = PolicyLogger.getLogger()
	
	#Mappings	
        #Mappings contains the basic association between keywords and objects, functions or static values
        #Note that these mappings are ONLY defined by the lib user (programmer) 
        _ConditionMappings = ControllerMappings.getConditionMappings()
	_ActionMappings = ControllerMappings.getActionMappings()

	#RuleTable default atributes
	#All rules created, moved or updated will be in a RuleTable with the atributes below
	_defaultName = 'provisioning'
	_defaultPersistence = 'Django'
	_defaultParser = 'RegexParser'
	_persistenceFlag = True
	_policyType = True #True: Accept; False:Deny
 	
	#Main methods 
#	@staticmethod
#        def getInstance(name = None):
#		if not name:
#			name = RuleTableManager._tableName
#		if CreatedRuledTables.objects.filter(name=name):
#               	return RuleTableManager.getRuleTable(name,mapps)
#		else: 
#			CreateModel = CreatedRuledTables(name = name, uuid = uuid.uuid4().hex)
#                	CreateModel.save()
#			return RuleTableManager.load(name)

	@staticmethod
	def getInstance(name=None):
		if not name:
			name = RuleTableManager._defaultName
		mapps = dict()
                mapps.update(RuleTableManager.getConditionMappings())
                mapps.update(RuleTableManager.getActionMappings())
		sorted(mapps.iterkeys())
		
		with RuleTableManager._mutex:
			RuleTableManager._instance = RuleTable.loadOrGenerate(name, mapps, RuleTableManager._defaultParser, RuleTableManager._defaultPersistence, RuleTableManager._persistenceFlag, RuleTableManager._policyType, uuid.uuid4().hex)
				
		return RuleTableManager._instance

        '''
        Deletes the instance of PolicyRuleTable for a given ID.
        This method should be seldom used.
        '''
        @staticmethod
        def deleteInstance(tableID=None):
            if tableID:
                backend = RuleTableManager._defaultPersistence
                with RuleTableManager._mutex:
                    RuleTable.delete(tableID, backend)

	'''
	Retrieves all instances of PolicyRuleTable for a given name.
	This method should be seldom used.
	'''
        @staticmethod
        def getAllInstances(name=None):
                if not name:
                        name = RuleTableManager._defaultName
		backend = RuleTableManager._defaultPersistence
                with RuleTableManager._mutex:
			instances = RuleTable.loadAll(name, backend)
		return instances

	#RuleTableMethods
	@staticmethod
	def AddRule(string,enabled=True,pos=None,parser=None,pBackend=None,persist=True, tableName=None):
		return RuleTableManager.getInstance(tableName).addRule(string,enabled,pos,parser,pBackend,persist)

	@staticmethod
	def RemoveRule(rule=None, index=None,tableName=None):
		return RuleTableManager.getInstance(tableName).removeRule(rule, index)
	
	@staticmethod
	def MoveRule(newIndex,rule=None,oldIndex=None,tableName=None):
		return RuleTableManager.getInstance(tableName).moveRule(newIndex,rule,oldIndex)

	@staticmethod
	def EnableOrDisableRule(ruleUUID,tableName=None):
		enabled = RuleTableManager.getRuleOrIndexOrIsEnabled(ruleUUID,'Enabled',tableName)
	        index = RuleTableManager.getRuleOrIndexOrIsEnabled(ruleUUID,'Index',tableName)
        	if enabled:
                	RuleTableManager.DisableRule(None,index,tableName)
                
        	else:
                	RuleTableManager.EnableRule(None,index,tableName)

		return RuleTableManager.getInstance(tableName)

	@staticmethod
	def editRule(rule,enable,priority,PreviousPriority,tableName):

                #When the IM is editing a Rule, a new one is added to the top of the ruleSet(the edited rule).That rule is in a known position.
                #Then the "old rule" is removed. This rule was in previousPriority + 1 beacuse of the addition of the edited rule
                #Finally the edited rule in pos. 0 is moved to the priority position
                #This aproach is maked in this way to avoid to lose the removed Rule if the edited rule raises any exception.
                RuleTableManager.AddRule(rule,enable,0, None, None,False,tableName)
                RuleTableManager.RemoveRule(None,(int(PreviousPriority)+1),tableName)
                RuleTableManager.MoveRule(priority,None,0)
	
	@staticmethod
	def deleteRule(ruleUUID,tableName):
        	ruleSet = RuleTableManager.GetRuleSet(tableName)
        	for rule in ruleSet:
                	if str(rule.rule.getUUID()) == ruleUUID:
                        	index = ruleSet.index(rule)
                        	RuleTableManager.RemoveRule(None,index,tableName)

	@staticmethod
	def EnableRule(rule=None,index=None,tableName=None):
		ruleTable = RuleTableManager.getInstance(tableName)
		return ruleTable.enableRule(rule,index)

	@staticmethod
        def DisableRule(rule=None,index=None,tableName=None):
               	ruleTable = RuleTableManager.getInstance(tableName)
		return ruleTable.disableRule(rule,index)
		

	@staticmethod
	def SetPolicy(policy,tableName=None):
                return RuleTableManager.getInstance(tableName).setPolicy(policy)

	@staticmethod
	def Evaluate(metaObj, tableName=None):
		try:
			RuleTableManager.getInstance(tableName).evaluate(metaObj)
		except Exception as e:
			RuleTableManager.logger.error("Denied policy: %s" %(e))
			#if isinstance(e, MultiplePolicyObjectsReturned):
			if issubclass(type(e), MultiplePolicyObjectsReturned):
				send_mail(
					settings.EMAIL_SUBJECT_PREFIX + "DB error: multiple Policy tables",
					"There are multiple PolicyTables with the same name in your SQL engine.\nPlease do ensure this is not happening by checking the contents of:\n\n    database: %s\n    table: pypelib_RuleTableModel\n\n" % (settings.DATABASE_NAME),
					from_email=settings.DEFAULT_FROM_EMAIL,
					recipient_list=[settings.ROOT_EMAIL],
					)
				RuleTableManager.logger.info("E-mail sent to Island Manager. Reason: multiple Policy tables")
			# Policy denial raises Exception to avoid VM resources allocation
			raise e

                RuleTableManager.logger.debug("All policies were accepted")
                return

	#getters
	@staticmethod
	def GetRuleSet(tableName = None):
                return RuleTableManager.getInstance(tableName).getRuleSet()
	
	@staticmethod
        def GetName(tableName = None):
                return RuleTableManager.getInstance(tableName).getName()

	@staticmethod
        def GetPolicyType(tableName = None):
                return RuleTableManager.getInstance(tableName).getPolicyType()

	@staticmethod
        def GetPersistence(tableName = None):
                return RuleTableManager.getInstance(tableName).getPersistence()

	@staticmethod
        def GetParser(tableName = None):
                return RuleTableManager.getInstance(tableName).getParser()

	@staticmethod
        def GetResolverMappings(tableName = None):
                return sorted(RuleTableManager.getInstance(tableName).getResolverMappings().iterkeys())

	@staticmethod
        def GetPersistenceFlag(tableName = None):
                return RuleTableManager.getInstance(tableName).getPersistenceFlag()


	#@staticmethod
	#def getModelConditions(tableName):
	#	conditions = list()
	#	print tableName
	#	
	#	conditionModel =ConditionModel.objects.filter(ruletable = tableName)
	#	for cond in conditionModel:
	#		conditions.append(cond.condition)
	#		
	#	return conditions
	#@staticmethod
	#def saveCondition(string, table):
	#	conditionModel = ConditionModel(condition = string, ruletable = table)
	#	conditionModel.save()
	#	return
			
	@staticmethod		
	def getConditionMappings():
		return RuleTableManager._ConditionMappings

	@staticmethod
	def getActionMappings():
		return RuleTableManager._ActionMappings

	@staticmethod	
	def getDefaultName():
		return RuleTableManager._defaultName
	@staticmethod
	def UpdateRuleTablePolicy(policy,tableName=None):
		if policy == 'accept':
                	RuleTableManager.SetPolicy(True,tableName)
        	else:
                	RuleTableManager.SetPolicy(False,tableName)
	
	#Useful Provisioning Methods
        @staticmethod
        def getRuleOrIndexOrIsEnabled(ruleID,Mode,tableName=None):


                if Mode not in ['Rule','Index','Enabled']:
                        raise Exception ('Unrecognized Mode. Only three modes are allowed: Rule, Index and Enabled')
		
		ruleList = RuleTableManager.getInstance(tableName).getRuleSet()
                for rule in ruleList:
                        if str(rule.rule.getUUID()) == str(ruleID):
                                if Mode == 'Rule':
                                        return rule.rule
                                if Mode == 'Index':
                                        return ruleList.index(rule)
                                if Mode == 'Enabled':
                                        return rule.enabled
                raise Exception('Cannot edit the rule. The rule you are looking for does not exist')

	@staticmethod
        def getPriorityList(name = None):
                RuleSetLength = len(RuleTableManager.getInstance(name)._ruleSet)
                i = 0
                out = []
                while i < RuleSetLength:
                        out.append(i)
                        i += 1
                return out

	@staticmethod
	def getValue(rule):
        	types = ['accept','deny']
        	if rule._type['value']:
                	value = 'accept'
        	else:
                	value = 'deny'
        	types.pop(types.index(value))
        	return value, types
	
	@staticmethod
	def getType(rule):
        	terminals = ['terminal','nonterminal']
        	if rule._type['terminal']:
                	value = 'terminal'
        	else:
                	value = 'nonterminal'
        	terminals.pop(terminals.index(value))
        	return value, terminals

	@staticmethod
	def SetConditionList(rule,conditions):
        	condition = rule.getConditionDump()
        	for cond in conditions:
                	if condition.replace(" ","")== cond.replace(" ", ""):
                	        conditions.pop(conditions.index(cond))
        	return condition, conditions

	@staticmethod
	def SetActionList(rule,mapps):
        	try:
                	action = rule.getMatchAction()
        	except:
                	action = "None"
		if action == None:
			action = "None"
        	keys = mapps.keys()
        	for act in keys:
                	if action.replace(" ","") == act.replace(" ",""):
        	                keys.pop(keys.index(act))
	        return action, keys

	@staticmethod
	def SetPriorityList(rule, tableName=None):
        	Rules = RuleTableManager.GetRuleSet(tableName)
        	PriorityList = RuleTableManager.getPriorityList()
        	for Rule in Rules:
                	if rule.dump() == Rule.rule.dump():
                        	index = Rules.index(Rule)
                        	for num in PriorityList:
                                	if index == num:
                                        	PriorityList.pop(PriorityList.index(num))
        	return index, PriorityList

#	@staticmethod
#	def setDefaultRule(RAM,NVMS,name=None):
#
#		RuleTableManager.getInstance()
#
#		if not RuleTableManager.getRuleSet():

#			if RuleTableManager.GetPolicyType():
#				operator = '>'
#				value = 'deny'
#			else:
#				operator = '<='
#				value = 'accept'

#			rule = 'if ((number.vms %s %s) && (vm.memory_mb %s %s)) then %s  denyMessage You cannot request more than %s vms or %sMBytes/vm #Main Rule' %(operator,NVMS,operator,RAM,value,NVMS,RAM) 
		
#			RuleTableManager.AddRule(rule)
