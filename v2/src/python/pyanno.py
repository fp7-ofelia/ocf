
"""
Pyanno Python Annotations

version 0.76

Uses the new python decorators feature.

Do not apply these annotations within this module.

charlesmchen@gmail.com

for documentation, see the index.html file included in the distribution.

http://fightingquaker.com/pyanno/

"""

#from __future__ import with_statement

import types, inspect, sys

try:
    from sip import wrappertype
    USE_SIP = True
except:
    wrappertype = None
    USE_SIP = False

'''
Runtime checking can be disabled with this global.
'''
DO_RUNTIME_VALIDATION = True

"""
The constants can be used in place of the type constants defined in the python "types" module.
"""
selfType = 'selfType'  # singleton placeholder constant
classType = 'classType'  # singleton placeholder constant
ignoreType = 'ignoreType'
callableType = 'callableType'

"""
ClassName can be used to avoid circular imports and other illegal references.
See documentation.
"""
class ClassName:
    def __init__(self, classname):
        self.classname = classname
    
    def __str__(self):
        return self.classname

"""
Exceptions thrown by the Pyanno annotations
"""

class AnnotationException(Exception):
    def __init__(self, description):
        description = __getCallerDescription__() + description
        Exception.__init__(self, description)

class AnnotationMethodError(AnnotationException):
    def __init__(self, description):
        AnnotationException.__init__(self, description)

class AbstractMethodError(AnnotationException):
    def __init__(self, description):
        AnnotationException.__init__(self, description)

class PrivateMethodError(AnnotationException):
    def __init__(self, description):
        AnnotationException.__init__(self, description)

class ProtectedMethodError(AnnotationException):
    def __init__(self, description):
        AnnotationException.__init__(self, description)

class ReturnTypeError(AnnotationException):
    def __init__(self, description):
        AnnotationException.__init__(self, description)

class ParamTypeError(AnnotationException):
    def __init__(self, description):
        AnnotationException.__init__(self, description)

PYANNO_ERRORS = (ParamTypeError, 
                             ReturnTypeError, 
                             AbstractMethodError, 
                             AnnotationMethodError, 
                             PrivateMethodError,
                             ProtectedMethodError,
                             )

"""
-----------------------------------------------------
"""

def __annotationHasArguments__(positionalParameters, keywordParameters):
    if len(keywordParameters) == 0 and len(positionalParameters) == 1 and type(positionalParameters[0]) is types.FunctionType:
        return False
    return True

def __copyPropertiesToWrapper__(func, wrapper):
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__
    wrapper.__module__ = func.__module__


'''
This annotation does no checking; strictly for commenting purposes
'''
def noopAnnotation(*positionalParameters, **keywordParameters):
    if not __annotationHasArguments__(positionalParameters, keywordParameters):
        func = positionalParameters[0]
        __addAnnotationDoc__(func, '@noopAnnotation', '@noopAnnotation ' + str(positionalParameters) \
                             + ', ' + str(keywordParameters) + '')
        return func

    if len(positionalParameters) > 0 or len(keywordParameters) > 0:
        raise AnnotationMethodError('noop method annotation doesn\'t accept arguments.')
    
    def decorator(func):
        __addAnnotationDoc__(func, '@noopAnnotation', '@noopAnnotation ' + str(positionalParameters) \
                             + ', ' + str(keywordParameters) + '')
        return func
    return decorator

class __privateMethodDecorator__:

    def __init__(self, funcModule):
        self.__funcModule__ = funcModule
        
    def __call__(self, func):
        if not DO_RUNTIME_VALIDATION:
            return func
        
        def wrapper(*positionalValues, **keywordValues):
            stack = inspect.stack()
            callerFrame = stack[1]
            callerModule = callerFrame[1]
            if callerModule != self.__funcModule__:
                raise PrivateMethodError("Private method called from another module: " + callerModule)
            
            return func(*positionalValues, **keywordValues)
        
        wrapper.__privateMethod__ = True
    
        __copyPropertiesToWrapper__(func, wrapper)
    
        __addAnnotationDoc__(func, '@privateMethod', '@privateMethod')
    
        wrapper.__wrappedFunction__ = func
    
        argspec = __getFunctionArgumentsRecursive__(func)
        wrapper.__func_argspec__ = argspec
        
        return wrapper

'''
This annotation throws an error if the decorated function is called from another module.
'''
def privateMethod(*positionalParameters, **keywordParameters):

    stack = inspect.stack()
    if len(stack) < 2:
        raise PrivateMethodError("Couldn\'t retrieve stack.")
    callerFrame = stack[1]
    callerModule = callerFrame[1]
    
    if not __annotationHasArguments__(positionalParameters, keywordParameters):
        func = positionalParameters[0]
        return __privateMethodDecorator__(callerModule)(func)

    if len(positionalParameters) > 0 or len(keywordParameters) > 0:
        raise AnnotationMethodError('private method annotation doesn\'t accept arguments.')

    return __privateMethodDecorator__(callerModule)



class __protectedMethodDecorator__:

    def __init__(self, funcModule):
        self.__funcModule__ = funcModule
        
    def __call__(self, func):
        if not DO_RUNTIME_VALIDATION:
            return func
        
        def wrapper(*positionalValues, **keywordValues):
            stack = inspect.stack()
            callerFrame = stack[1]
            callerModule = callerFrame[1]
            if callerModule != self.__funcModule__:
                import os.path
                if os.path.dirname( callerModule ) != os.path.dirname( self.__funcModule__ ):
#                    print 'funcPackage ', funcPackage 
#                    print 'callerModule', callerModule, self.__funcModule__
                    raise ProtectedMethodError("Protected method called from another module: " + callerModule)
            
            return func(*positionalValues, **keywordValues)
    #        raise ProtectedMethodError("Abstract Method called.")
        wrapper.__protectedMethod__ = True
    
        __copyPropertiesToWrapper__(func, wrapper)
    
        __addAnnotationDoc__(func, '@protectedMethod', '@protectedMethod')
    
        wrapper.__wrappedFunction__ = func
    
        argspec = __getFunctionArgumentsRecursive__(func)
        wrapper.__func_argspec__ = argspec
        
        return wrapper

'''
This annotation throws an error if the decorated function is called from a module in another package.
'''
def protectedMethod(*positionalParameters, **keywordParameters):

    stack = inspect.stack()
    if len(stack) < 2:
        raise ProtectedMethodError("Couldn\'t retrieve stack.")
    callerFrame = stack[1]
    callerModule = callerFrame[1]
    
    if not __annotationHasArguments__(positionalParameters, keywordParameters):
        func = positionalParameters[0]
        return __protectedMethodDecorator__(callerModule)(func)

    if len(positionalParameters) > 0 or len(keywordParameters) > 0:
        raise AnnotationMethodError('protected method annotation doesn\'t accept arguments.')

    return __protectedMethodDecorator__(callerModule)

'''
This annotation does no checking; strictly for commenting purposes.

This decorator expects its arguments to be a list of exceptions.
'''
def raises(*positionalParameters, **keywordParameters):
    if not __annotationHasArguments__(positionalParameters, keywordParameters):
        func = positionalParameters[0]
        __addAnnotationDoc__(func, '@raises', '@raises ' + str(positionalParameters) \
                             + ', ' + str(keywordParameters) + '')
        return func

    if len(keywordParameters) > 0:
        raise AnnotationMethodError('raises method annotation doesn\'t accept keyword arguments.')
    
    exceptions = []
    for positionalParameter in positionalParameters:
        if not issubclass(positionalParameter, BaseException):
            raise AnnotationMethodError('arguments to raises method annotation must be Exceptions (a subclass of BaseException).' )
        if positionalParameter in exceptions:
            raise AnnotationMethodError('Exception appears twice in arguments to @raises annotation: '  + positionalParameter.__name__) 
        exceptions.append( positionalParameter )
    
    def decorator(func):
        __addAnnotationDoc__(func, '@raises', '@raises ' + str(positionalParameters) \
                             + ', ' + str(keywordParameters) + '')
        return func
    return decorator

def __addAnnotationDoc__(func, key, value):
    if not hasattr(func, '__annotation_docs__'):
        func.__annotation_docs__ = {}
    func.__annotation_docs__[key] = value

def __abstractMethodDecorator__(func):
    if not DO_RUNTIME_VALIDATION:
        return func
    
    def wrapper(*positionalValues, **keywordValues):
        raise AbstractMethodError("Abstract Method called.")
    wrapper.__abstractMethod__ = True

    __copyPropertiesToWrapper__(func, wrapper)

    __addAnnotationDoc__(func, '@abstractMethod', '@abstractMethod')

    wrapper.__wrappedFunction__ = func

    argspec = __getFunctionArgumentsRecursive__(func)
    wrapper.__func_argspec__ = argspec
    
    return wrapper

'''
This annotation raises an exception if the decorated function is ever called.
'''
def abstractMethod(*positionalParameters, **keywordParameters):

    if not __annotationHasArguments__(positionalParameters, keywordParameters):
        func = positionalParameters[0]
        return __abstractMethodDecorator__(func)

    if len(positionalParameters) > 0 or len(keywordParameters) > 0:
        raise AnnotationMethodError('abstract method annotation doesn\'t accept arguments.')

    return __abstractMethodDecorator__

def __deprecatedMethodDecorator__(func):
    if not DO_RUNTIME_VALIDATION:
        return func
    
    def wrapper(*positionalValues, **keywordValues):
        print str(func.__name__) + ' is deprecated.'
        func(*positionalValues, **keywordValues)
    wrapper.__deprecatedMethod__ = True

    __copyPropertiesToWrapper__(func, wrapper)

    __addAnnotationDoc__(func, '@deprecatedMethod', '@deprecatedMethod')

    wrapper.__wrappedFunction__ = func

    argspec = __getFunctionArgumentsRecursive__(func)
    wrapper.__func_argspec__ = argspec
    
    return wrapper

'''
This annotation prints a warning if the decorated function is ever called.
'''
def deprecatedMethod(*positionalParameters, **keywordParameters):

    if not __annotationHasArguments__(positionalParameters, keywordParameters):
        func = positionalParameters[0]
        return __deprecatedMethodDecorator__(func)

    if len(positionalParameters) > 0 or len(keywordParameters) > 0:
        raise AnnotationMethodError('deprecated method annotation doesn\'t accept arguments.')

    return __deprecatedMethodDecorator__


def __dumpFunc__(func, prefix = ''):
    print
    if len(prefix) > 0:
        prefix += ' '
    print prefix + "__dumpFunc__ " + str(func) + " " + str(type(func))
    print prefix + '\t' + "__call__" + str(func.__call__) + " " + str(type(func.__call__))
    for name in dir(func):
        if hasattr(func, name):
            print prefix + "\t" + str(name) + ": " + str(getattr(func, name))
        else:
            print prefix + "\t" + str(name)
    print 
    
def __ParamErrorFactory__(funcName, msg):
    return ParamTypeError(funcName + " received " + msg)

def __noParamsDecorator__(func):
    if not DO_RUNTIME_VALIDATION:
        return func

    def wrapper(*positionalValues, **keywordValues):
        
        if len(positionalValues) >  0 or len(keywordValues) > 0:
            raise ParamTypeError(func.__name__ + ' has no arguments: ' + str(positionalValues) + \
                                  ', ' + str(keywordValues))
        
        return func(*positionalValues, **keywordValues)
    
    __copyPropertiesToWrapper__(func, wrapper)

    __addAnnotationDoc__(wrapper, '@parameterTypes', '@parameterTypes None')
    
    argspec = __getFunctionArgumentsRecursive__(func)
    wrapper.__func_argspec__ = argspec
    wrapper.__wrappedFunction__ = func

    return wrapper
    
def __getFunctionArgumentsRecursive__(func):
    if hasattr(func, '__func_argspec__'):
        argspec = getattr(func, '__func_argspec__')
    else:
        argspec = inspect.getargspec(func)
    
    return argspec
      
'''
This annotation does runtime type-checking on the arguments passed to the decorated function.
'''
def parameterTypes(*positionalParameters, **keywordParameters):

    if keywordParameters:
        raise AnnotationMethodError('Don\'t annotate parameter types with keywords.')

    if not __annotationHasArguments__(positionalParameters, keywordParameters):
        func = positionalParameters[0]
        return __noParamsDecorator__(func)

    if not positionalParameters and not keywordParameters:
        return __noParamsDecorator__

    
    def decorator(func):
        if not DO_RUNTIME_VALIDATION:
            return func

        argspec = __getFunctionArgumentsRecursive__(func)
   
        #__dumpFunc__(func)
        #print "noResultDecorator: " + str(func) + " " + str(type(func))
    
        def wrapper(*positionalValues, **keywordValues):
            
            try:
                
                # charles, we want more unique names than __parsedParamTypes__ and __unparsedParamTypes__
                if not hasattr(func, '__parsedParamTypes__'):
                    #print 'parsing params'
                    #__dumpFunc__(func)
                    func.__parsedParamTypes__ = __parseParamTypes__(func.__name__, func.func_globals, argspec, func.__unparsedParamTypes__)
                positionalTypes, keywordTypes = func.__parsedParamTypes__
                '''
                print func.__name__ + ' param ' + "__unparsedParamTypes__: " + str(func.__unparsedParamTypes__) + " " + str(type(func.__unparsedParamTypes__))
                print func.__name__ + ' param ' + "correctTypes: " + str(correctTypes) + " " + str(type(correctTypes))
                '''
                __checkParamTypes__(func.__name__, __ParamErrorFactory__, positionalValues, keywordValues, positionalTypes, keywordTypes, argspec, False)
                
                return func(*positionalValues, **keywordValues)

            except BaseException, e:
                raise e
            
        wrapper.__func_argspec__ = argspec
        
        __copyPropertiesToWrapper__(func, wrapper)
        func.__unparsedParamTypes__ = positionalParameters
        
        __addAnnotationDoc__(wrapper, '@parameterTypes', '@parameterTypes ' + str(positionalParameters) \
                             + ', ' + str(keywordParameters) + '')

        return wrapper
    
    return decorator



def __checkParamType__(funcName, errorFactory, values, correctTypes, i, value, correctType, debug = False):
    
    # is none always okay?
    if type(value) is types.NoneType:
        return

    errorMsg = "unexpected value["+str(i)+"]: " 
#                            + str(value) 
    if type(value) == types.InstanceType:
        errorMsg += ' (' + str(value.__class__) + ')'
    else:
        errorMsg += ' (' + str(type(value)) + ')'
    errorMsg += ", expected: " + str(correctType) \
                            + " (" + str(values) + "), expected: " + str(correctTypes) \
                            + " "
    errorFactoryArgs = (funcName, errorMsg, )

    
    # can we validate this assertoin more narrowly and check the class type?
    if correctType is selfType:
        # correctType = types.InstanceType
        return 
    elif correctType is ignoreType:
        return
    elif correctType is classType:
        correctType = types.ClassType
    
    global USE_SIP
    if USE_SIP and type(correctType) is wrappertype:
        if type(type(value)) is wrappertype:
            if not isinstance(value, correctType):
                raise errorFactory(*errorFactoryArgs)
            return
        raise errorFactory(*errorFactoryArgs)

    if isinstance(correctType, ClassName):
        
        if USE_SIP and type(type(value)) is wrappertype:
            pass
        elif type(value) is types.InstanceType:
            pass
        else:
            raise errorFactory(*errorFactoryArgs)

        # declared classname must match name of class or superclass.

        mro = inspect.getmro(value.__class__)
        for item in mro:
            #print 'item.__name__', item.__name__
            if item.__name__ == correctType.classname:
                return
        raise errorFactory(*errorFactoryArgs)
    
    
    #if type(value) == types.InstanceType and type(correctType)  == types.ClassType:
    if type(correctType)  == types.ClassType:
        if not isinstance(value, correctType):
            raise errorFactory(*errorFactoryArgs)
        return
    
    
    if type(correctType) is dict:
        keyType = correctType.keys()[0]
        valueType = correctType[keyType]
        if type(value) is not dict:
            raise errorFactory(*errorFactoryArgs)
        for key in value.keys():
            __checkParamType__(funcName, errorFactory, values, correctTypes, i, key, keyType, debug)
#            print 'value[key]', value, type(value), key, type(key)
            subvalue = value[key]
            __checkParamType__(funcName, errorFactory, values, correctTypes, i, subvalue, valueType, debug)
        return
    elif type(correctType) in (tuple, list):
        if type(value) is not type(correctType):
            raise errorFactory(*errorFactoryArgs)
        elemType = correctType[0]
        for elem in value:
            __checkParamType__(funcName, errorFactory, values, correctTypes, i, elem, elemType, debug)
        return
    elif correctType is str:
        if type(value) in (str, unicode):
            return
        raise errorFactory(*errorFactoryArgs)
    elif correctType is float:
        if type(value) in (int, float):
            return
        raise errorFactory(*errorFactoryArgs)
    elif correctType is callableType:
        if callable(value):
            return
#        if type(value) in (types.BuiltinFunctionType, types.BuiltinMethodType, types.FunctionType, \
#                           types.GeneratorType, types.LambdaType, types.MethodType, \
#                           types.UnboundMethodType):
#            return
        raise errorFactory(*errorFactoryArgs)
    elif type(value) == correctType:
        return
    
    #be more specific about tuple index
    #print 'problem: ' + funcName +" correctTypes: " + str(correctTypes)
    raise errorFactory(*errorFactoryArgs)
    
    


    
def __normalizeValues__(funcName, errorFactory, positionalValues, keywordValues, \
                              positionalTypes, keywordTypes, argspec, debug = False):

#    debug = True
    if debug:
        print "__normalizeValues__ funcName: "  + funcName
        print "__normalizeValues__ argspec: "  + str(argspec) + " "  + str(type(argspec))

    args = argspec[0]
    varargs = argspec[1]
    varkw = argspec[2]
    defaults = argspec[3]
    
    totalValues = len(positionalValues) 
    if keywordValues:
        totalValues += len(keywordValues)

    if totalValues > len(args):
        raise ParamTypeError( funcName + ': function too many arguments: ' + str(positionalValues) + ', ' + str(keywordValues))
        
    #charles: TODO: not handling varargs, varkw
    if debug:
        print '\t', 'args', funcName, args
        print '\t', 'varargs', funcName, varargs
        print '\t', 'varkw', funcName, varkw
        print '\t', 'defaults', funcName, defaults
    
    if not defaults:
        requiredParamCount = len(args) 
    else:
        requiredParamCount = len(args) - len(defaults)

    if debug:
        print '\t', 'requiredParamCount', funcName, requiredParamCount

    requiredValues = []
    optionalValues = {}
    
    if len(positionalValues) > requiredParamCount:
        for index in xrange(len(positionalValues)):
            value = positionalValues[index]
            if index < requiredParamCount:
                requiredValues.append(value)
            else:
                #if index >= len(args):
                argname = args[index]
                optionalValues[argname] = value 

        for keyword in keywordValues:
            if keyword in optionalValues:
                raise ParamTypeError('more than one value for paramter: ' + keyword) 
                
            optionalValues[keyword] = keywordValues[keyword]
    
    else:
        requiredValues.extend(positionalValues)
        keywords = keywordValues.keys()
        if debug:
            print '\t', 'keywords', funcName, keywords, type(keywords)
        
        while len(requiredValues) < requiredParamCount:
            index = len(requiredValues)
            argname = args[index]
            if debug:
                print '\t', 'argname', funcName, argname
            if argname not in keywords:
                raise ParamTypeError('function missing required argument: ' + argname)
            value = keywordValues[argname]
            keywords.remove(argname)
            requiredValues.append(value)
        
        for keyword in keywords:
            optionalValues[keyword] = keywordValues[keyword]
        
    if debug:
        print 'requiredValues', requiredValues
        print 'optionalValues', optionalValues
        
    return requiredValues, optionalValues
    
def __checkParamTypes__(funcName, errorFactory, positionalValues, keywordValues, \
                              positionalTypes, keywordTypes, argspec, debug = False):
    
    #debug = True
    if debug:
        print "checkTypes positionalValues: "  + str(positionalValues) + " "  + str(type(positionalValues))
        print "checkTypes keywordValues: "  + str(keywordValues) + " "  + str(type(keywordValues))
        print "checkTypes positionalTypes: "  + str(positionalTypes) + " "  + str(type(positionalTypes))
        print "checkTypes keywordTypes: "  + str(keywordTypes) + " "  + str(type(keywordTypes))

    positionalValues, keywordValues = __normalizeValues__(funcName, errorFactory, positionalValues, keywordValues, \
                              positionalTypes, keywordTypes, argspec, debug)

    if debug:
        print "checkTypes positionalValues: "  + str(positionalValues) + " "  + str(type(positionalValues))
        print "checkTypes keywordValues: "  + str(keywordValues) + " "  + str(type(keywordValues))
    debug = False
        
    __checkValueTypes__(funcName, errorFactory, positionalValues, keywordValues, \
                              positionalTypes, keywordTypes, debug)
    
def __checkValueTypes__(funcName, errorFactory, positionalValues, keywordValues, \
                              positionalTypes, keywordTypes, debug = False):
    
    if debug:
        print "checkTypes positionalValues: "  + str(positionalValues) + " "  + str(type(positionalValues))
        print "checkTypes keywordValues: "  + str(keywordValues) + " "  + str(type(keywordValues))
        print "checkTypes positionalTypes: "  + str(positionalTypes) + " "  + str(type(positionalTypes))
        print "checkTypes keywordTypes: "  + str(keywordTypes) + " "  + str(type(keywordTypes))

    if not positionalTypes:
         if positionalValues:
            raise errorFactory(funcName, "unexpected positional arguments (" + str(positionalValues) + ")")
    else:
         if not positionalValues:
            raise errorFactory(funcName, "missing positional arguments (" + str(positionalValues) + ")")
        
         if len(positionalValues) != len(positionalTypes):
            print "checkTypes positionalValues: "  + str(positionalValues) + " "  + str(type(positionalValues))
            print "checkTypes keywordValues: "  + str(keywordValues) + " "  + str(type(keywordValues))
            print "checkTypes positionalTypes: "  + str(positionalTypes) + " "  + str(type(positionalTypes))
            print "checkTypes keywordTypes: "  + str(keywordTypes) + " "  + str(type(keywordTypes))
            
            if len(positionalValues) < len(positionalTypes):
                raise errorFactory(funcName, "missing positional arguments (" + str(positionalValues) + ")")
            else:
                raise errorFactory(funcName, "unexpected positional arguments (" + str(positionalValues) + ")")

         for index in range(len(positionalValues)):
             positionalValue = positionalValues[index]
             positionalType = positionalTypes[index]

             __checkParamType__(funcName, errorFactory, positionalValues, positionalTypes, index, \
                                  positionalValue, positionalType, debug)

    if keywordValues:
        if not keywordTypes:
            raise errorFactory(funcName, "unexpected keyword arguments (" + str(keywordValues) + ")")
        
        for keyword in keywordValues:
            keywordValue = keywordValues[keyword]
            
            if keyword not in keywordTypes:
                raise errorFactory(funcName, "unexpected keyword argument (" + str(keyword) + ": " + \
                                    str(keywordValue) + ")")
            keywordType = keywordTypes[keyword]

            __checkParamType__(funcName, errorFactory, keywordValues, keywordTypes, keyword, \
                                  keywordValue, keywordType, debug)

           
def __checkResultTypes__(funcName, errorFactory, values, positionalTypes, debug = False):
    
    if len(positionalTypes) == 1:
        # special case.  returned results not always in a tuple
        values = [ values ] 
        
    keywordTypes = None # return values don't use keywords.
    __checkValueTypes__(funcName, errorFactory, values, None, positionalTypes, keywordTypes, debug)

def __ReturnErrorFactory__(funcName, msg):
    
    return ReturnTypeError(funcName + " returned " + msg)

def __parseStringType__(func_name, func_globals, typeString, checkForSelfType):

    result = []

    if checkForSelfType:
        typeString = typeString.strip()
        #print "checkForSelfType: " + typeString
        selfTypeName = 'selfType'
        if typeString.startswith(selfTypeName):
            result.append(selfType)
            typeString = typeString[len(selfTypeName):]
            #print "checkForSelfType: " + typeString
            typeString = typeString.strip()
            canBeEmpty = True
            if len(typeString)>0:
                if typeString[0] != ',':
                    raise AnnotationMethodError(func_name + ': Missing comma after selfType: ' + str(typeStrings))
                typeString = typeString[1:]
            
    
    typeString = typeString.strip()
    #print '\t\t'+"__parseStringType__: " + str(typeString) + " " + str(type(typeString))
    if len(typeString) < 1:
        return result
    
    #print '\t\t'+"__parseStringType__: " + str(typeString) + " " + str(type(typeString))
    evals = eval('[' + typeString + ']', func_globals)
    for evaled in evals:
        #print '\t\t\t'+"evaled.1: " + str(evaled) + " " + str(type(evaled))
        result.append(__parseType__(func_name, evaled))
    return result 
        
def __parseType__(func_name, arg):

    #print '\t'+"arg: " + str(arg) + " " + str(type(arg))
    if arg in (selfType, ignoreType, classType, callableType) :
        return arg
    elif isinstance(arg, ClassName):
        return arg
    elif type(arg) is types.TypeType:
        return arg
    elif type(arg) is types.ClassType:
        return arg
    elif USE_SIP and type(arg) is wrappertype:
        return arg
    elif type(arg) is dict:
        keys = arg.keys()
        if len(keys) == 0:
            return dict
        if len(keys) > 1:
            raise AnnotationMethodError(func_name + ': Unknown annotation argument: ' + str(arg) + " " + str(type(arg)))
        key = keys[0]
        __parseType__(func_name, key)
        value = arg[key]
        __parseType__(func_name, value)
        return arg
    elif type(arg) in (tuple, list,):
        if len(arg) == 0:
            return type(arg)
        if len(arg) > 1:
            raise AnnotationMethodError(func_name + ': Unknown annotation argument: ' + str(arg) + " " + str(type(arg)))
        __parseType__(func_name, arg[0])
        return arg
    else:
        raise AnnotationMethodError(func_name + ': Unknown annotation argument: ' + str(arg) + " " + str(type(arg)))



def __parseReturnTypes__(func_name, func_globals, rawTypes):

#    return __parseReturnTypes__(func_name, func_globals, args, False)

    checkForSelfType = False

#    if True:
#        print '\t'+"__parseReturnTypes__ rawTypes: " + str(rawTypes) + " " + str(type(rawTypes))

    parsedTypes = __evaluateTypes__(func_name, func_globals, rawTypes, checkForSelfType)

#    if True:
#        print '\t'+"__parseReturnTypes__ parsedTypes: " + str(parsedTypes) + " " + str(type(parsedTypes))
    
    requiredTypes = parsedTypes
    optionalTypes = {}
    return requiredTypes, optionalTypes

def __parseExceptionTypes__(func_name, func_globals, rawTypes):

    checkForSelfType = False
    parsedTypes = __evaluateTypes__(func_name, func_globals, rawTypes, checkForSelfType)

    requiredTypes = parsedTypes
    optionalTypes = {}
    return requiredTypes, optionalTypes


def __parseParamTypes__(func_name, func_globals, argspec, rawTypes):
    checkForSelfType = True
    
#    print 'argspec', argspec, type(argspec)
    argumentNames = argspec[0]
    varargs = argspec[1]
    varkw = argspec[2]
    defaults = argspec[3]

#    print '\t', 'argumentNames', argumentNames
#    print '\t', 'varargs', varargs
#    print '\t', 'varkw', varkw
#    print '\t', 'defaults', defaults
    
#    annotation argument: \'' + str(rawPositionalType) + "'")
    
#    if True:
#        print '\t'+"__parseParamTypes__ rawTypes: " + str(rawTypes) + " " + str(type(rawTypes))

    parsedTypes = __evaluateTypes__(func_name, func_globals, rawTypes, checkForSelfType)

#    if True:
#        print '\t'+"__parseParamTypes__ parsedTypes: " + str(parsedTypes) + " " + str(type(parsedTypes))

    if len(parsedTypes) < len(argumentNames):
        raise AnnotationMethodError(func_name + ': Missing param types (' + 
                                    str(len(rawTypes)) + ' < ' + str(len(argumentNames))
                                    + ')')
    elif len(parsedTypes) > len(argumentNames):
        raise AnnotationMethodError(func_name + ': Missing param types (' + 
                                    str(len(rawTypes)) + ' > ' + str(len(argumentNames))
                                    + ')')
    
    if not defaults:
        requiredParamCount = len(argumentNames) 
    else:
        requiredParamCount = len(argumentNames) - len(defaults)

    requiredParams = []
    for index in xrange(requiredParamCount):
        requiredParams.append(parsedTypes[index])
        
    optionalParams = {}
    if defaults:
        for index in xrange(len(defaults)):
            optionalParams[argumentNames[requiredParamCount+index]] = parsedTypes[requiredParamCount+index]

#    if False:
#        print '\t'+"__parseParamTypes__ requiredParams: " + str(requiredParams) + " " + str(type(requiredParams))
#        print '\t'+"__parseParamTypes__ optionalParams: " + str(optionalParams) + " " + str(type(optionalParams))

    return requiredParams, optionalParams


def __evaluateTypes__(func_name, func_globals, rawTypes, checkForSelfType):

    parsedTypes = []
    isFirstParsedType = True
    for rawType in rawTypes:
        if type(rawType) is str:
            parsed = __parseStringType__(func_name, func_globals, rawType, \
                                           checkForSelfType and isFirstParsedType)
            if parsed is None:
                #if not canBeEmpty:
                if len(rawTypes) > 1:
                    raise AnnotationMethodError(func_name + ': Unknown annotation argument: \'' + str(rawParsedType) + "'")
                # okay to pass empty string if only arg.  means no types.
                continue
            parsedTypes.extend(parsed)
        else:
            parsedTypes.append(__parseType__(func_name, rawType))
        
        isFirstParsedType = False
    
    if False:
        print '\t'+"__evaluateTypes__ parsedTypes: " + str(parsedTypes) + " " + str(type(parsedTypes))

    return parsedTypes

def __noResultDecorator__(func):
    if not DO_RUNTIME_VALIDATION:
        return func

    #__dumpFunc__(func)
    #print "noResultDecorator: " + str(func) + " " + str(type(func))

    def wrapper(*positionalValues, **keywordValues):
        
        result = func(*positionalValues, **keywordValues)
        
        if result is not None:
            raise ReturnTypeError(func.__name__ + ' should not return a value: ' + str(result))
        
        
        return result
    
    __copyPropertiesToWrapper__(func, wrapper)

    __addAnnotationDoc__(wrapper, '@returnType', '@returnType None')

    wrapper.__wrappedFunction__ = func

    argspec = __getFunctionArgumentsRecursive__(func)
    wrapper.__func_argspec__ = argspec
    
    return wrapper


def __getCallerDescription__():
    
    stack = inspect.stack()
    callerFrame = None
    for index in xrange(len(stack)):
        frame = stack[index]
        module = frame[1]
        if __file__ != module:
            callerFrame = frame
            break
    
    if not callerFrame:
        print 'missing callerFrame!'
        callerFrame = stack[0]
        
#    print'frame', frame
    callerModule = callerFrame[1]
#    print'callerModule', callerModule
    import os.path
    callerModuleName = os.path.basename(callerModule)
#    print'callerModuleName', callerModuleName
    callerLine = callerFrame[2]
#    print'callerLine', callerLine
    callerDescription = callerModuleName + '(' + str(callerLine) + '): '
#    print 'callerDescription', callerDescription
    return callerDescription

'''
This annotation does runtime type-checking on the values returned by the decorated function.
'''
def returnType(*positionalParameters, **keywordParameters):
    '''
    use like this: 
    @returnType
    def aMethodThatReturnsNothing(self):
        pass

    @returnType ()
    def aMethodThatReturnsNothing(self):
        pass

    @returnType ( int ) 
    def aMethodThatReturnsAnInt(self):
        pass
    '''
   
    if True:
#    try:
        
        if keywordParameters:
            raise AnnotationMethodError( 'return values can\'t have keywords.')
            
        if not __annotationHasArguments__(positionalParameters, keywordParameters):
            func = positionalParameters[0]
            return __noResultDecorator__(func)
    
        if not positionalParameters and not keywordParameters:
            return __noResultDecorator__
    
        #unparsedReturnTypes = args
        
        def decorator(func):
            if not DO_RUNTIME_VALIDATION:
                return func
        
            #__dumpFunc__(func)
            #print "noResultDecorator: " + str(func) + " " + str(type(func))
        
            def wrapper(*positionalValues, **keywordValues):
                
                try:
                    values = func(*positionalValues, **keywordValues)
                    
                    # charles, we want more unique names than __parsedReturnTypes__ and __unparsedReturnTypes__
                    if not hasattr(func, '__parsedReturnTypes__'):
                        #print 'parsing'
                        #__dumpFunc__(func)
                        func.__parsedReturnTypes__ = __parseReturnTypes__(func.__name__, func.func_globals, func.__unparsedReturnTypes__)
                    positionalTypes, keywordTypes = func.__parsedReturnTypes__
                    '''
                    print "__unparsedReturnTypes__: " + str(func.__unparsedReturnTypes__) + " " + str(type(func.__unparsedReturnTypes__))
                    print "correctTypes: " + str(correctTypes) + " " + str(type(correctTypes))
                    '''
                    __checkResultTypes__(func.__name__, __ReturnErrorFactory__, values, positionalTypes, False)
                    
                    return values
                except BaseException, e:
                    raise e
#                    raise e, None, sys.exc_info()[2]
            
            __copyPropertiesToWrapper__(func, wrapper)
            func.__unparsedReturnTypes__ = positionalParameters
            __addAnnotationDoc__(wrapper, '@returnType', '@returnType ' + str(positionalParameters) \
                                 + ', ' + str(keywordParameters) + '')
    
            argspec = __getFunctionArgumentsRecursive__(func)
            wrapper.__func_argspec__ = argspec
            
            return wrapper
        
        return decorator

#    except AnnotationException, e:
#
#    #    frame = inspect.currentframe()
#        from utils.Debug import dirDebug
#    #    dirDebug('frame', frame)
#    #    frameinfo = inspect.getframeinfo(frame)
#    ##    dirDebug('frameinfo', frameinfo)
#    #    print'frameinfo', frameinfo
#    
#        stack = inspect.stack()
#        print'stack', stack
#        frame = stack[1]
#    #    dirDebug('frame', frame)
#        print'frame', frame
#        callerModule = frame[1]
#        print'callerModule', callerModule
#        callerLine = frame[1]
#        print'callerLine', callerLine
#    
##    frameinfo = inspect.getframeinfo(frame)
###    dirDebug('frameinfo', frameinfo)
##    print'frameinfo', frameinfo
#    
##    raise Exception('')
#        tb = sys.exc_info()[2]     
#        while True:
#            tbframe = tb.tb_frame
#            print'tbframe', tbframe
#            tbframeinfo = inspect.getframeinfo(tbframe)
#            print'tbframeinfo', tbframeinfo
#            tbframeModule = tbframeinfo[0]
##            tbframeModule', tbframeModule
#            import os.path
#            modulename = os.path.basename(tbframeModule)
#            print'modulename', modulename
#            print 'dir', dir()
#            print '__file__', __file__
#            print __file__ == tbframeModule
#            break
#        
#        print 'tb', tb
#        dirDebug('tb', tb)
#        raise e, None, sys.exc_info()[2]        
