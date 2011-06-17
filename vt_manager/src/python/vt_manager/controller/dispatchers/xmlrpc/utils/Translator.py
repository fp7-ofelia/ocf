from vt_manager.models import *

from vt_manager.models.Action import Action
import copy
import uuid
from vt_manager.controller.actions.ActionController import ActionController
class Translator():

	@staticmethod
	def xenVMtoModel(VMxmlClass, callBackURL, save):
		name = VMxmlClass.name
		uuid = VMxmlClass.uuid
		projectId = VMxmlClass.project_id
		projectName = VMxmlClass.project_name
		sliceId = VMxmlClass.slice_id
		sliceName = VMxmlClass.slice_name
		osType = VMxmlClass.operating_system_type
		osVersion = VMxmlClass.operating_system_version
		osDist = VMxmlClass.operating_system_distribution
		memory = VMxmlClass.xen_configuration.memory_mb
		callBackUrl = callBackURL
		hdSetupType = VMxmlClass.xen_configuration.hd_setup_type
		print "[LEODEBUG] HD SETUP TYPE EN TRANSLATOR"
		print VMxmlClass.xen_configuration.hd_setup_type
		hdOriginPath = VMxmlClass.xen_configuration.hd_origin_path
		virtSetupType = VMxmlClass.xen_configuration.virtualization_setup_type
		return name,uuid,projectId,projectName,sliceId,sliceName,osType,osVersion,osDist,memory,None,None,callBackUrl,hdSetupType,hdOriginPath,virtSetupType,save

	@staticmethod
	def ActionToModel(action, hyperaction, save = "noSave" ):
		actionModel = Action()
		actionModel.hyperaction = hyperaction
		if not action.status:
			actionModel.status = 'QUEUED'
		else:
			actionModel.status = action.status
		actionModel.type = action.type_
		actionModel.uuid = action.id
		if save is "save":
			actionModel.save()
		return actionModel

