"""
Intermediary for the AM resources, so each plugin may access the resources
corresponding to another AM. Data needed: plugin name, class name, search filter.

@date: Mar 13, 2013
@author: leonardo.bergesio@i2cat.net
"""

#from django.conf import settings 
from django.db.models import Q
from utils import join_paths, Singleton
import os
from urls import PLUGIN_LOADER

class PluginCommunicator():

    """
    Allows different pluggins in the same Expedient to ask resources to each other.
    Basic requirement is so that a plugin can ask to some other plugin the id of a resource (node)
    it has to build the links between resources.
    """
    # Allows only one instance of this class
    __metaclass__ = Singleton

    @staticmethod
    def get_objects(slice, plugin_type, klass, **kwargs):
        """
        Retrieves the id of a model belonging to another plugin
        and which is contained in the same slice than the 
        AM corresponding to the other plugin that invokes this.

        E.g. Slice "test" with "VT test AM" and "OF test AM"
             VT plugin will ask for OF resources whose AM ("OF
             AM test") was previously added to slice "tests".
        """
        try:
#            plugins_modules = settings.PLUGIN_LOADER.plugin_settings.get(plugin_type).get("general").get("aggregate_plugins")[0]
            plugins_modules = PLUGIN_LOADER.plugin_settings.get(plugin_type).get("general").get("aggregate_plugins")[0]
            p_agg = plugins_modules.split('.')[-1]
            p_models_path = '.'.join(plugins_modules.split('.')[:-1])
            try:
                model = getattr(__import__(p_models_path,fromlist=[klass]), klass)
            except:    
                try:  
                    model = getattr(__import__(p_models_path+'.'+klass,fromlist=[klass]), klass)
                except:
                    pass    
            # Filters resources by slice (will not return any aggregate's resource from another slice)
            objects = model.objects.filter(**kwargs)
            #print "objects: %s" % str(objects)
            for obj in objects:
                if not (obj != None and obj.aggregate in slice._get_aggregates()):
                    raise Exception
            return objects
        except Exception,e:
            print "[ERROR] PluginCommunicator could not obtain object. Details: %s " % str(e)
            return None

    @staticmethod
    def get_object(slice, plugin_type, klass, **kwargs):
        objects = PluginCommunicator.get_objects(slice, plugin_type, klass, **kwargs)
        try:
            return objects[0]
        except Exception,e:
            print "[ERROR] PluginCommunicator could not obtain object. Details: %s " % str(e)
            return None

    @staticmethod
    def get_object_id(slice, plugin_type, klass, **kwargs):    
        try:
            return PluginCommunicator.get_object(slice, plugin_type, klass, **kwargs).id
        except:
            return None
 
