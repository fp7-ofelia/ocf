import os
import sys

from django.conf import settings

'''
        @author: omoya

        OCF Expedient User Theme Manager 
'''

class ExpedientThemeManager():
	
	#Settings main attributes
        _theme = '/' + settings.THEME
        _mediaDir = settings.MEDIA_ROOT
        _templateDir = settings.TEMPLATE_DIRS[0]
        _srcDir = settings.SRC_DIR
	_default = 'default'

	#Useful dict to translate a viewname from a django url to a path
        _pathFromView = {'img_media':'/img/','css_media':'/css/','js_media':'/js/'}
	
	#get The static path required to urls.py
        @staticmethod
        def getStaticThemeTuple(staticName):
                return str(ExpedientThemeManager._theme[1:] ) + '_' + str(staticName),  '/..' + str(ExpedientThemeManager._theme) + str(ExpedientThemeManager._pathFromView[staticName])

	#Static method used by the URL custom templatetag
        @staticmethod
        def getThemeStaticUrl(viewname, args):

                if ExpedientThemeManager._theme[1:] == ExpedientThemeManager._default:
                        return viewname
                if not len(args)==1:
                        #Static paths only contain ONE argument, so probably this is a common url
                        return viewname
                if  not viewname in  ExpedientThemeManager._pathFromView.keys():
                        #common url: no change in viewname, total transparency with dynamic urls 
                        return viewname

                path = str(ExpedientThemeManager._mediaDir) + str(ExpedientThemeManager._theme) + '/' + str(ExpedientThemeManager._pathFromView[viewname]) + str(args[0]).replace("'","")
                #flag os.F_OK is to test the existence of the path
                if os.access(path,os.F_OK):
                        viewname = ExpedientThemeManager._theme[1:] + '_' + viewname

                return viewname

	@staticmethod
	def initialize():

		#setting up TEMPLATE_DIRS to support themes	
		if not ExpedientThemeManager._theme == ExpedientThemeManager._default:
			ThemeTemplateDirs = ExpedientThemeManager.setThemeTemplateDirs()
			settings.TEMPLATE_DIRS = ThemeTemplateDirs + settings.TEMPLATE_DIRS
		
		#loading url templatetag
		from django.template.loader import add_to_builtins
		add_to_builtins('expedient.common.utils.templatetags.url')
	
	@staticmethod
	def setThemeTemplateDirs():

		themetemplates = list()
		for path in settings.TEMPLATE_DIRS:
			splitpath = path.split('/')
			try:
				splitpath[splitpath.index(ExpedientThemeManager._default)]= ExpedientThemeManager._theme
			except:
				#Transparency with non-containing /default/ dir templates
				pass

			themetemplates.append('/'.join(splitpath))
		return themetemplates
