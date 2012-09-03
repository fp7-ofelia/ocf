import sys
import os
import re

from django.conf import settings

'''
        @author: omoya

        OCF VT AM User Theme Manager 
'''

class ThemeManager():
	
	#Settings main attributes
	_theme = '/' + settings.THEME 
	_mediaDir = settings.MEDIA_ROOT
	_templateDir = settings.TEMPLATE_DIRS[0]
	_srcDir = settings.SRC_DIR	

	#Useful dict to translate a viewname from a djano url to a path
	_pathFromView = {'img_media':'/images/','css_media':'/css/','js_media':'/js/','fancybox':'/fancybox/'}	

	#Static method used by the URL custom templatetag
	@staticmethod
	def getThemeStaticUrl(viewname, args):
		
		if ThemeManager._theme[1:] == 'ofelia':
			return viewname
		if not len(args)==1:
			#Static paths only contain ONE argument, so probably this is a common url
			return viewname
		if  not viewname in  ThemeManager._pathFromView.keys():
			#common url: no change in viewname, total transparency with dynamic urls 
			return viewname
		
		path = str(ThemeManager._mediaDir) + str(ThemeManager._theme) + '/' + str(ThemeManager._pathFromView[viewname]) + str(args[0]).replace("'","")		              
		#flag os.F_OK is to test the existence of the path
		if os.access(path,os.F_OK):
			viewname = ThemeManager._theme[1:] + '_' + viewname
		return viewname

	#get The static path required to urls.py
	@staticmethod
	def getStaticThemeTuple(staticName):
		return str(ThemeManager._theme[1:] )+ '_' + str(staticName),  str(ThemeManager._theme) + str(ThemeManager._pathFromView[staticName])

	#Set the Template_dirs in the correct hierarchy if necessary and import the custom templatetags
	@staticmethod
	def initialize():
		
		#setTemplateDirs

		theme_templates = ThemeManager.getThemeTemplatePath(ThemeManager._templateDir)
		
		
		if not (theme_templates[0] == settings.TEMPLATE_DIRS[0]):
			settings.TEMPLATE_DIRS = (theme_templates,) + settings.TEMPLATE_DIRS #theme_templates need tuple conversion

		#Load the custom URL templatetag
		from django.template.loader import add_to_builtins
		add_to_builtins('vt_manager.views.templatetags.url')

	@staticmethod
	def getThemeTemplatePath(strPath):
	
		#TODO:It is possible to have only one template_dir in TEMPLATE_DIRS?	
		templateDirSplit = strPath.split('/')		
		
		#Remove all '' elements of the list
		for i in range(templateDirSplit.count('')):
			templateDirSplit.remove('')
		#Remove the last element (Default)
		templateDirSplit.pop(len(templateDirSplit)-1)
		templateDirSplit.append(str(ThemeManager._theme[1:]))
		return "/"+"/".join(templateDirSplit)
