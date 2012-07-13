import uuid
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, HttpResponse
from django.views.generic import simple
#from vt_manager.controller.policyEngine.Condition import *
#from vt_manager.controller.policyEngine.Rule import *
from vt_manager.controller.drivers.VTDriver import VTDriver
from vt_manager.models import *
#from vt_manager.controller.policyEngine.RuleTable import *
from pypelib import RuleTable
from vt_manager.controller.policies.RuleTableManager import *


@login_required
def policy(request):
        '''
                The policy view function
        '''
	if (not request.user.is_superuser):

        	return simple.direct_to_template(request,
                                                 template = 'not_admin.html',
                                                 extra_context = {'user':request.user},
                                                )

        else: #Admin
		
		RuleTableName = None
		tableList =  RuleTableManager.getNameNUUID()
		tableName = request.POST.get("ruleTables")
                CurrentTable = request.POST.get("current_table")

		if tableName == None:
			LoadedTable = False
			RuleList = list()#RuleTable.getRuleSet().rule
		else: 
			LoadedTable = True
			RuleTable = RuleTableManager.load(tableName)
			RuleList = RuleTable.getRuleSet()
			RuleTableName = RuleTable.name

		
			
		return simple.direct_to_template(request,
                                          template = 'policyEngine/policy.html',
                                          extra_context = {'user': request.user,
                                                           'tables': tableList,
                                                           'CurrentTable': tableName,
							   'RuleTable': RuleTableName},
                                         )
def rule_table_view(request, TableName = None):

        if TableName == None:
                tableList =  RuleTableManager.getNameNUUID()
                try:
                        firstTable = tableList[0]
                        TableName = firstTable['name']
                except:
                        print "No RuleTables created yet:"
                        TableName = 'RuleTable1'
                        print TableName,"will be created..."

        table = RuleTableManager.load(TableName)

        return simple.direct_to_template(request,
                                         template = 'policyEngine/table_view.html',
                                         extra_context = {'user': request.user,
                                                          'table':table},
                                  )

def edit_ruleset(request, TableName ):
	
	table = RuleTableManager.load(TableName)

	return simple.direct_to_template(request,
                                         template = 'policyEngine/edit_ruleset.html',
                                         extra_context = {'user': request.user,
                                                   	  'table':table},
                                  )


def policy_create(request,table):

	errors = []
        rules = []
        tables =  RuleTableManager.getRuleTableList()
	ruleTable = RuleTableManager.load(table)
	maps = RuleTableManager.getActionMappings()
	conditions = RuleTableManager.getModelConditions(table)
	priority = RuleTableManager.getPriorityList(ruleTable)

	return simple.direct_to_template(request,
                                          template = 'policyEngine/policy_create.html',
                                          extra_context = {'user': request.user,
                                                           'tables': tables,
                                                           'rules':rules,
                                                           'CurrentTable': table,
							   'mappings':maps,
							   'conditions':conditions,
							   'priorityList':priority,
							   'allMappings':RuleTableManager.getResolverMappings(ruleTable),
							   'ConditionMappings':RuleTableManager.getConditionMappings(),
                                                           'ActionMappings':RuleTableManager.getActionMappings(),
                                                           'errors': errors},
                                        )

def rule_create(request):

	errors = list()
	formMode = request.POST.get("conditionMode")
	tableName = request.POST.get("table")
	PreviousPriority = request.POST.get("ppriority")
        editing = request.POST.get("editing")
        ruleid = request.POST.get("uuid")
        ruleCondition = request.POST.get("condition")
        ruleDesc = request.POST.get("description")
        ruleError = request.POST.get("error_message")
        ruleType = request.POST.get("type")
        ruleAction = request.POST.get("action")
        ruleValue = request.POST.get("value")
        rulePriority = request.POST.get("priority")
        ruleEnable = request.POST.get("enable")
        previousTable = request.POST.get("hidden_name")
	expertRule = request.POST.get("expertRule")
	newConditions = request.POST.get("conditionID")	
	saved = request.POST.get("saved")

	print newConditions
	condition_save(newConditions.split('*'),tableName)

        if rulePriority == 'Last' or rulePriority == '':
                priority = None
        else:
                priority = int(rulePriority)

	#Avoid empty fields

        if ruleDesc == "":
                errors.append("Description Field is empty")
        if ruleError == "":
                errors.append("Error Message field is empty")
        if ruleCondition == "":
                errors.append("Condition field is empty")
	

        if request.POST.get("enable") == 'enable':
           enable = True

        else:
           enable = False

	if ruleType == "terminal":
		ruleType = ""

#Rule String convertion required
	if formMode == "easy":
        	rule = "if " + ruleCondition +  " then " + ruleValue + " " + ruleType  + " do " + ruleAction + " denyMessage " + ruleError + " #" + ruleDesc
	else:
		rule = expertRule

        strings = rule
	
	try:
		if errors:
                        raise Exception("")	
		ruleTable =  RuleTableManager.load(tableName)
		print "Request.Condition got", ruleCondition, strings
		if editing == '1':
                	print 'editing...'
                	if previousTable == tableName:
				try:
					ruleTable.addRule(strings,enable,priority, None, None, persist=False)
#					ruleTable.removeRule(None,int(PreviousPriority))
					ruleTable.removeRule(None,0)
#					ruleTable.addRule(strings,enable,priority)
				except Exception as e:
					print "CARDEBUG. Algo ha fallado: ", e
					raise e
                	else:
                        	print 'Changing table...'
                        	ruleTable.addRule(strings,enable,priority)
                        	print 'successful add to ' + tableName
                        	ruleTable = RuleTable.LoadOrGenerate(previousTable,resolverMappings, 'RegexParser', 'Django', True, pType, RuleTableUUID )
                        	ruleTable.removeRule(None,int(PreviousPriority))
                        	print 'remove from ' +  previousTable + ' successful'
        	else:
                	ruleTable.addRule(strings,enable,priority)

		tableDB = RuleTableManager.getRuleTableList()
                load = True
                F = 'create'
                return HttpResponseRedirect("rule_table_view")#rule_table_view(tableName)		

	except Exception as e:
		print "CARDEBUG exception: ", e
		errors.insert(0,e)
		errors.insert(0,"The Rule cannot be generated. Reason(s):")
		ruleTable = RuleTableManager.load(tableName)
		priority = RuleTableManager.getPriorityList(ruleTable)
		actionList = SetActionList(ruleAction,RuleTableManager.getActionMappings())
		priority = RuleTableManager.getPriorityList(ruleTable)
		try:
			int(rulePriority)
			if int(rulePriority) in priority:
				priority.pop(priority.index(int(rulePriority)))
		except:
			rulePriority = "Last"

		if ruleValue == "accept":
			value2 = ["deny"]
		else:
			value2 = ["accept"]

		if ruleType == "nonterminal":
			type2 = ["terminal"]
		else:
			ruleType = "terminal"
			type2 = ["nonterminal"]

		if saved == "True" or ruleid == "":

			return simple.direct_to_template(request,
        	        	template = 'policyEngine/policy_create.html',
                		extra_context = {'user': request.user,
						 'saved':True,
						 'CurrentTable':tableName,
                                        	 'priority':priority,
	                                         'enabled':ruleEnable,
        	                                 'valueS':ruleValue,
                	                         'valueD':value2,
                        	                 'terminalS':ruleType,
                                	         'terminalD':type2,
	                                         'errorMsg':ruleError,
        	                                 'description':ruleDesc,
                                	         'condition':ruleCondition,
                	                         'conditions':RuleTableManager.getModelConditions(tableName),
                        	                 'conditionList':"",
	                                         'action':ruleAction,
        	                                 'actionList':actionList[1],
                	                         'PrioritySel':rulePriority,
                                	         'priorityList':priority,
                        	                 'allMappings':RuleTableManager.getResolverMappings(ruleTable),
	                                         'ConditionMappings':RuleTableManager.getConditionMappings(),
        	                                 'ActionMappings':RuleTableManager.getActionMappings(),
                	                         'errors': errors,
						 'rule_uuid':ruleid,}
                        	                         )
		else:
			return rule_edit(request, ruleid, tableName, errors)

def enable_disable(request, rule_uuid, table_name):

	ruleTable = RuleTableManager.load(table_name)
	rule = RuleTableManager.getRule(ruleTable,rule_uuid)

	if rule[2] == True:
		print "let's see", rule[2]
		ruleTable.disableRule(rule[0])
		
	else:
		ruleTable.enableRule(rule[0])


	#return simple.direct_to_template(request,
        #                                 template = 'policyEngine/table_view.html',
        #                                 extra_context = {'user': request.user,
        #                                                  'table':ruleTable},
        #                          )
	return HttpResponseRedirect("/rule_table_view")	
	
	

def condition_create(request, TableName):
	ruleTable = RuleTableManager.load(TableName)
	return simple.direct_to_template(request,
                                          template = 'policyEngine/condition_create.html',
                                          extra_context = {'user': request.user,
							   'tableName' : TableName,
							   'mappings' : RuleTableManager.getConditionMappings(),
							   'conditions' : RuleTableManager.getModelConditions(TableName)},
                                        )

def condition_save(conditionList,table):

	for cond in conditionList:
		if cond != '':
			RuleTableManager.saveCondition(cond,table)
	
	return

def rule_delete(request):
	
	rule_uuid = request.POST.get("uuid")
        Table_Name = request.POST.get("table_name")
        tableDB = RuleTableManager.getRuleTableList()
	RuleTable = RuleTableManager.load(Table_Name)
        for rule in RuleTable.getRuleSet():
		print rule_uuid
                if str(rule.rule.getUUID()) == rule_uuid:
			print 'Rule Founded'
                        index = RuleTable._ruleSet.index(rule)
                        RuleTable.removeRule(None,index)
			print RuleTable.dump()

	return HttpResponseRedirect("rule_table_view")
#	return simple.direct_to_template(request,
#                                                 template = 'policyEngine/table_view.html',
#                                                 extra_context = {'user': request.user,
#                                                                  'table': RuleTable},
#                                                )
	
def update_ruleTable_policy(request):
	policy = request.POST.get("defaultPolicy")
	Table_Name = request.POST.get("table_name")
	RuleTable = RuleTableManager.load(Table_Name)
	if policy == 'accept':
		RuleTable.setPolicy(True)
	else:
		RuleTable.setPolicy(False)
	return HttpResponseRedirect("rule_table_view")
#	return simple.direct_to_template(request,
#						template = 'policyEngine/table_view.html',
#						extra_context = {'user': request.user,
#						                 'table': RuleTable},
#						)



def rule_edit(request, rule_uuid, table_name, errors=None):

	ruleTable = RuleTableManager.load(table_name)
        
	rule = RuleTableManager.getRule(ruleTable,rule_uuid)
	rulevalues = getValue(rule[0])
	ruletypes = getType(rule[0])
	#Flag to be able to diferenciate edit state from creating estate                
        edit = True
        tables = RuleTableManager.getRuleTableList()
	conditions = RuleTableManager.getModelConditions(table_name)
	CondList = SetConditionList(rule[0],conditions)
	actionList = SetActionList(rule[0],RuleTableManager.getActionMappings())
	priorityList = SetPriorityList(rule[0], ruleTable)
	error = str(rule[0].getErrorMsg())
	description = str(rule[0].getDescription())


	return simple.direct_to_template(request,
                                                 template = 'policyEngine/policy_create.html',
                                                 extra_context = {'user':request.user,
                                                                  'edit':edit,
                                                                  'tables':tables,
                                                                  'rule':rule[0],
                                                                  'priority':rule[1],
								  'enabled':rule[2],
                                                                  'valueS':rulevalues[0],
                                                                  'valueD':rulevalues[1],
                                                                  'terminalS':ruletypes[0],
                                                                  'terminalD':ruletypes[1],
                                                                  'rule_uuid':rule_uuid,
								  'ptable':table_name,
								  'errorMsg':error,
								  'description':description,
								  'condition':CondList[0],
								  'conditions':conditions,
								  'conditionList':CondList[1],
								  'action':actionList[0],
								  'actionList':actionList[1],
								  'PrioritySel':priorityList[0], 
								  'priorityList':priorityList[1],
								  'allMappings':RuleTableManager.getResolverMappings(ruleTable),
								  'ConditionMappings':RuleTableManager.getConditionMappings(),
								  'ActionMappings':RuleTableManager.getActionMappings(),
                                                                  'CurrentTable':table_name,
								  'errors':errors},
                                        )

def rule_table(request):


	 return simple.direct_to_template(request,
                                                 template = 'policyEngine/policy_RuleTableCreate.html',
                                                 extra_context = {'user':request.user,
                                                                 },


                                                )

def rule_table_create(request):

	TableName = request.POST.get("tableName")
        TableType = request.POST.get("tableType")
        TablePersistence = request.POST.get("Persistence")
        TableParser = request.POST.get("Parser")
        TableMappings = request.POST.get("mappings")
        TableRuleSet = request.POST.get("rule_set")
        doPersistence = request.POST.get("persistence_flag")
        TableUUID = uuid.uuid4().hex
        TableSave = request.POST.get("save")

        if doPersistence == 'do_persistence':
                PersistenceFlag = True
        else:
                PersistenceFlag = False

        if TableType == "":
                TableType = False
        else:
                TableType = True

        if TableMappings == "":
                TableMappings = {}
        else:
                TableMappings = {}


        if  TableName == None:
                pass

        else:
		print TablePersistence	
		RuleTableManager.createRuleTables(TableName,TableMappings,TableParser, TablePersistence, PersistenceFlag, TableType,TableUUID)

                return policy(request)


	return simple.direct_to_template(request,
                                                 template = 'policyEngine/policy_RuleTableCreate.html',
                                                 extra_context = {'user':request.user,
                                                                 },


                                                )

def getRuleFormFields(RuleList, rule_uuid):

        print rule_uuid
        pos = 0
        for rule in RuleList:
                print rule.rule.getConditionDump()
                if rule.rule.getUUID() == rule_uuid:
                        return rule.rule,pos
                pos += 1
        raise Exception('Cannot load this Rule')

def getValue(rule):

	types = ['accept','deny']
	if rule._type['value']:
		value = 'accept'
	else:
		value = 'deny'

	types.pop(types.index(value))

	return value, types

def getType(rule):

        terminals = ['terminal','nonterminal']
        if rule._type['terminal']:
                value = 'terminal'
        else:
                value = 'nonterminal'

        terminals.pop(terminals.index(value))

        return value, terminals	
def SetConditionList(rule,conditions):

	condition = rule.getConditionDump()
	for cond in conditions:
		if condition.replace(" ","")== cond.replace(" ", ""):
			conditions.pop(conditions.index(cond))
	return condition, conditions

def SetActionList(rule,maps):
	try:
		action = rule.getMatchAction()
	except:
		action = rule
	keys = maps.keys()
	for act in keys:
		if action.replace(" ","") == act.replace(" ",""):
			keys.pop(keys.index(act))
	return action, keys

def SetPriorityList(rule,ruleTable):
	Rules = RuleTableManager.getRuleSet(ruleTable)
	PriorityList = RuleTableManager.getPriorityList(ruleTable)
	for Rule in Rules:
		if rule.dump() == Rule.rule.dump():
			index = Rules.index(Rule)
			for num in PriorityList:
				if index == num:
					PriorityList.pop(PriorityList.index(num))
	return index, PriorityList

