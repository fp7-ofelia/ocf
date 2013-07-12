from datetime import datetime, timedelta

import amsoil.core.pluginmanager as pm

import dummyexceptions as dummy_exception

worker = pm.getService('worker')

class DummyResourceManager():

    config = pm.getService("config")

    def __init__(self):
	pass

    def do_something(self):
	return "Dummy Resource Manager"

    def do_something_else(self):
	return "something cool"

