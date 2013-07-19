"""
Created on Jun 30, 2013

@author: CarolinaFernandez
"""

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.views.generic import simple
from common.permissions.shortcuts import has_permission, must_have_permission
from common.utils.plugins.pluginloader import PluginLoader
import re
import subprocess
#import logging
#logger = logging.getLogger("Administration")

TEMPLATE_PATH = "templates"
# Indicates the Nth last lines to be read from any log.
# Same as 'tail -LOG_N_LAST_LINES <log_file>'
LOG_N_LAST_LINES = 250
# Color for the log headers (e.g. date, type of message, ip)
LOG_HEADER_COLOR = "#444"

def home(request):
	"""
	Shows the Expedient administration panel.

	@param request HTTP request
	@return string template for administration panel
	"""
	must_have_permission(request.user, User, "can_manage_users")

	# Iterate over each plugin to get its administration data
	plugin_administration_methods = []
	for plugin in PluginLoader.plugin_settings:
		try:
			plugin_administration_methods.append([str(plugin.capitalize()), reverse("%s_administration" % str(plugin))])
		except:
			pass
#		except Exception as e:
#			print "[ERROR] Problem loading plugin administration methods inside administration module. Details: %s" % str(e)

	return simple.direct_to_template(
		request,
		template=TEMPLATE_PATH+"/index.html",
		extra_context={
			"breadcrumbs": (
				("Home", reverse("home")),
				("Administration", reverse("administration_home")),
			),
			"plugin_administration_methods": plugin_administration_methods,
		},
	)

def get_module_log_path(module_name):
	"""
	Obtains the physical path to the log of a given module.

	@param string name of a module
	@return string complete path to the log file for a given module
	"""
	module_log_path = ""
	try:
		if module_name == "expedient":
			module_log_path = "/var/log/ofelia/expedient/error.log"
		elif module_name == "openflow":
			module_log_path = "/var/log/ofelia/optin_manager/error.log"
		elif module_name == "virtualization":
			module_log_path = "/var/log/ofelia/vt_manager/error.log"
	except:
		pass
	return module_log_path

def view_log(request, module_name):
	"""
	Parses and shows log contents for a given module.

	@param request HTTP request
	@param string name of module
	@return string log contents for a given module
	"""
	must_have_permission(request.user, User, "can_manage_users")

	log_content = ""
	found_group = ""
	module_log_path = get_module_log_path(module_name)
	try:
		# Reads the Nth last lines from the log file
		module_log = open(module_log_path).read().splitlines()[-LOG_N_LAST_LINES:]
		for i, line in enumerate(module_log):
			while re.search("\[(.*?)\]", line):
				found_group = re.search("\[(.*?)\]", line).group(0)
				log_content += "<font color=\"%s\"><strong>%s</strong></font>" % (str(LOG_HEADER_COLOR), str(found_group))
				line = line.replace(found_group, "")
			log_content += line + "<br/>"
	except:
		log_content = "Not enough permissions to view %s log" % str(module_name).capitalize()

	return simple.direct_to_template(
		request,
		template=TEMPLATE_PATH+"/log.html",
		extra_context={
			"log_content": log_content,
		},
	)

def remove_log(request, module_name, option):
	"""
	Clears log contents for a given module.

	@param request HTTP request
	@param string name of module
	@return redirection back to the administration home
	"""
	must_have_permission(request.user, User, "can_manage_users")

	module_log_path = get_module_log_path(module_name)
	try:
		if option == "preserve":
			import datetime
			now = datetime.datetime.now()
			timestamp = "%s-%s-%s_%s:%s:%s" % (now.year, now.month, now.day, now.hour, now.minute, now.second)
			p = subprocess.Popen(["mv",module_log_path,
								"%s.%s" % (module_log_path, timestamp)], 
				stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			out, err = p.communicate()
		elif option == "clear":
			p = subprocess.Popen(["rm",module_log_path], 
				stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			out, err = p.communicate()
		# New log file is created regardless of chosen option
		if option:
			p = subprocess.Popen(["touch",module_log_path], 
				stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			out, err = p.communicate()
	except:
		pass

	return HttpResponseRedirect(reverse("administration_home"))

