"""
@date: Mar 13, 2013
@author: leonardo.bergesio@i2cat.net
"""

import os
from utils import join_paths, Singleton
#from pluginloader import PluginLoader
from django.conf import settings 
from django.db.models import Q

class PluginCommunicator():

	"""
	Allows different pluggins in the same Expedient to ask resources to each other.
	Basic requirement is so that a plugin can ask to some other plugin the id of a resource (node)
	it has to build the links between resources.
	"""
	# Allows only one instance of this class
	__metaclass__ = Singleton

	@staticmethod
	def get_object(plugin_type, klass, **kwargs):
        	"""
		Retrieves the id of a model belonging to another plugin.
        	"""

		try:
			plugins_modules = settings.PLUGIN_LOADER.plugin_settings.get(plugin_type).get("general").get("aggregate_plugins")[0]
			p_agg = plugins_modules.split('.')[-1]
			p_models_path = '.'.join(plugins_modules.split('.')[:-1])
	
			try:
				model = getattr(__import__(p_models_path,fromlist=[klass]), klass)
			except:	
				try:  
					model = getattr(__import__(p_models_path+'.'+klass,fromlist=[klass]), klass)
				except:
					pass
			object = model.objects.get(**kwargs)
			
			if object != None:
				return object
		
		except Exception,e:
			print "[ERROR] PluginCommunicator could not obtain object. Details: %s " % str(e)
			return -1


	@staticmethod
	def get_object_id(plugin_type, klass, **kwargs):	
		
		try:
			return PluginCommunicator.get_object(plugin_type, klass, **kwargs).id
		except:
			return -1
		
