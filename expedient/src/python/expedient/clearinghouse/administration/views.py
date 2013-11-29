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

TEMPLATE_PATH = "administration"#"templates/default"
# Indicates the Nth last lines to be read from any log.
# Size of of the buffer (in bytes) to return as a log'
LOG_N_BYTES_SIZE = 15000
# Color for the log headers (e.g. date, type of message, ip)
LOG_HEADER_COLOR = "#444"
LOGS_LOCATION = { "expedient": "/var/log/apache2/expedient/clearinghouse/error_log",
				  "vtam": "/var/log/apache2/vt_manager/error_log",
				  "ofam": "/var/log/apache2/openflow/optin_manager/error_log",
				  "foam": "/var/log/apache2/ofam/foam.log"}


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
			"logs_location":LOGS_LOCATION,
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
		module_log_path = LOGS_LOCATION[module_name]
	except Exception as e:
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
		module_log = get_log_chunk(open(module_log_path), LOG_N_BYTES_SIZE)  #open(module_log_path).read().splitlines()[-LOG_N_LAST_LINES:]
		for i, line in enumerate(module_log):
			while re.search("\[(.*?)\]", line):
				found_group = re.search("\[(.*?)\]", line).group(0)
				log_content += "<font color=\"%s\"><strong>%s</strong></font>" % (str(LOG_HEADER_COLOR), str(found_group))
				line = line.replace(found_group, "")
			log_content += line + "<br/>"
	except Exception as e:
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

def get_log_chunk(file_object, chunk_size=20000):
	"""
	Retrieve partial contents from a log.
	"""
	file_object.seek(-chunk_size,2) # Get the last chunk_size bytes starting from the end 
	return file_object.read(-chunk_size).splitlines()[1:] # Avoid showing truncated lines used by the seek pointer

