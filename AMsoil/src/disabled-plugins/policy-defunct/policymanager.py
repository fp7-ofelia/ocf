#from PolicyScope import PolicyScope
from pypelib.RuleTable import RuleTable
from exception import * 
from threading import Lock

class PolicyManager(object):

    '''
        Defines the interface to manage the diffent policy scopes.
        A Policy scope is defined as a table containing a set of
         rules that form an specific policy to a certain extend 
        (i.e. only to one user, only to one project, etc). PolicyMager 
        class registers the different scopes (rule tables) in a the 
        _scopes dictionary by its name (dict key).
        

    '''
    _scopes = {}
    _mutex = {}
    #Actually not needed if mappings from the initialize() method are 
    #directly passed and stored in the RuleTable
    #_mappings = {}
 
    @staticmethod
    def initialize(scopeName, mappings, parser, persistence, **kwargs):
        '''
            Initialize a specific Policy Scope by instantiating a 
            Rule Table and adding it to the PolicyManager registre _scopes
        '''

        if not scopeName in PolicyManager._scopes:
            PolicyManager._mutex[scopeName] = Lock()
            #PolicyManager._mappings[scopeName] = mappings
            with PolicyManager._mutex[scopeName]:
                PolicyManager._scopes[scopeName] = RuleTable.loadOrGenerate(scopeName, mappings, parser, persistence, True, **kwargs)
            return PolicyManager._scopes[scopeName]

    @staticmethod
    def getInstance(scopeName):
        '''
            Returns a specific RuleTable from the PolicyManager registre.
            If it is not present it throws UnexistingPolicyError.
        '''
        if not PolicyManager._scopes[scopeName]:
            raise UnexistingPolicyError(scopeName)
        else:
            with PolicyManager._mutex[scopeName]:
                return PolicyManager._scopes[scopeName]


    @staticmethod
    def evaluate(scopeName, obj):
        '''
            Evaluates the object obj against the rules in the scope. 
            Throws  TerminalMatch exception (defined in pypelib) if 
            obj does not fulfill the policy, which is replaced by the
            policy plugin's PolicyNotFulfilledError exception.
        '''

        try:
            return PolicyManager.getInstace(scopeName).evaluate(obj)
        except Exception,e:
            raise PolicyNotFulfilledError(scopeName)

    @staticmethod
    def dump(scopeName):
        '''
            Returns a string with the set of rules in the table of 
            the scope.
        '''
        return PolicyManager.getInstance(scopeName).dump()

    @staticmethod
    def clone(scopeName):
        return PolicyManager.getInstance(scopeName).clone()

    @staticmethod
    def addRule(scopeName,string,enabled=True,pos=None,parser=None,pBackend=None,persist=True):
        '''
            Adds a rule to a RuleTable.
        '''
        return PolicyManager.getInstance(scopeName).addRule(string,enabled,pos,parser,pBackend,persist)

    @staticmethod
    def removeRule(scopeName,rule=None, index=None):
        '''
            Removes a rule from a RuleTable.
        '''
        try:
            return PolicyManager.getInstance(scopeName).removeRule(rule, index)
        except Exception,e:
            raise PolicyException

    @staticmethod
    def moveRule(scopeName,newIndex, rule=None, index=None):
        '''
            Moves a rule within a RuleTable taking care of rearranging 
            the others present in the table.  
        '''
        try:
            return PolicyManager.getInstance(scopeName).moveRule(newIndex, rule, index)
        except Exception,e:
            raise PolicyException

    @staticmethod
    def enableRule(scopeName,rule=None, index=None):
        '''
            Activates a rule in the RuleTable.
        '''
        return PolicyManager.getInstance(scopeName).enableRule(rule, index)

    @staticmethod
    def disableRule(scopeName,rule=None, index=None):
        '''
            Deactivates a rule in the RuleTable.
        '''
        return PolicyManager.getInstance(scopeName).disableRule(rule, index)

### Decorators....

def PolicyInitialize(scopeName, mappings, parser, persistence, **kwargs):
    '''
        Definition of decorator @PolicyInitialize to be definied in 
        the setup() method of the plugin going to use PolicyManager
    '''
    PolicyManager.initialize(scopeName, mappings, parser, persistence, **kwargs)

def PolicyValidate(scopeName, obj):
    '''
        Definition of the decorator @PolicyValidate to be used by 
        the plugin which uses PolicyManager
    '''
    PolicyManager.evaluate(scopeName, obj)    



