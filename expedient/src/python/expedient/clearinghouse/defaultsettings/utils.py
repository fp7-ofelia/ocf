'''Contains functions to help with default settings
Created on Feb 14, 2011

@author: jnaous
'''
import os
import sys
# Retrieve current location and add parent's to system path (relative path > absolute path)
#sys.path.append("/opt/ofelia/expedient/src/python/expedient/clearinghouse/")
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))

def append_to_local_setting(setting_name, l, globals_dict, at_start=False):
    """Set or update a setting by adding items to it.
    
    If a setting with name C{EXTRA_%s} % C{setting_name} exists in C{localsettings}
    then this function will add append list C{l} to the value of
    EXTRA_C{setting_name}. The setting in C{localsettings} must be a list.
    This function will actually set the value in the module, so no need to
    reset it.
    
    @param setting_name: The name of the setting, to which an "EXTRA_" will
        be prepended.
    @type setting_name: C{str}
    @param l: list to append to the setting's value
    @type l: list
    @param globals_dict: the globals for the module calling the function
    @type globals_dict: C{dict}
    @keyword at_start: Should the list be inserted at the start?
        Default is False
    @type at_start: C{bool}
    
    @return: the value of the new setting.
    """
    
    import localsettings
    setting = getattr(localsettings, "EXTRA_%s" % setting_name, [])
    v = l + setting if at_start else setting + l
    _modname = globals_dict['__name__']
    _caller_mod = sys.modules[_modname]
    setattr(_caller_mod, setting_name, v)
    return v

def get_or_set_default(setting_name, default, globals_dict):
    """Get or set a default setting from localsettings.
    
    If the setting with name C{setting_name} is in localsettings, then
    use that as the default value. Otherwise, use C{default}. This function
    will actually set the value in the module, so no need to reset it.
    
    @param setting_name: The setting name to be set
    @type setting_name: C{str}
    @param default: The dafult value of the setting if not found.
    @type default: unspecified.
    @param globals_dict: the globals for the module calling the function
    @type globals_dict: C{dict}
    
    @return: The value that was set.
    """
    import localsettings
    if hasattr(localsettings, setting_name):
        v = getattr(localsettings, setting_name)
    else:
        v = default

    _modname = globals_dict['__name__']
    _caller_mod = sys.modules[_modname]
    
    setattr(_caller_mod, setting_name, v)
    return v
