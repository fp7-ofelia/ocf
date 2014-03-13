from django.core.exceptions import ValidationError
from django.views.generic.create_update import get_model_and_form_class


class HttpUtils():

	@staticmethod
	def getFieldInPost(request, attr , model = None, fieldIndex=0):
		attr = str(attr)
		if model !=None:
			try:
				getattr(model(), attr)
			except:
				raise Exception("Model %s has not attribute %s\n" %(str(model), attr))
		
		if len(request.POST[attr])< fieldIndex:
			raise Exception ("fieldIndex and request.POST length mismatch")
		elif fieldIndex != 0:
			return request.POST[attr][fieldIndex]
		
		return request.POST[attr]


	@staticmethod
	def getSameAttrLenInPost(request, attr):
		try:
			return len(request.POST.getlist(attr))
		except:
			raise Exception("There is no attribute called %s in the POST data" %attr)


	@staticmethod
	def processExceptionForm(e,request,modelClass):
		form = HttpUtils.getFormFromModel(modelClass)
		iform = form(request.POST)
		if len(iform.errors) > 0:
			string = ""
			for element in iform.errors: 
				string += iform.errors[element].as_text()
			iform.errors['__all__'] = "Error: " + string
		else:
			iform.errors['__all__'] = "Error: " + str(e)
		return iform
	
	@staticmethod
	def processException(e):
		if isinstance(e,ValidationError):
			return "Error:"+str(e)[3:-2]
		else:
			return "Error:"+str(e)
	
	@staticmethod
	def getInstanceFromForm(request,model):
		form = HttpUtils.getFormFromModel(model)
		iform = form(request.POST)
		instance = iform.save(commit = False)
		return instance

	@staticmethod
	def getFormFromModel(model, form_class=None):
		model, form_class = get_model_and_form_class(model, form_class)
		return form_class
	
	@staticmethod 
	def getFormFromInstance(instance,modelClass):
		formclass = HttpUtils.getFormFromModel(modelClass)
		return formclass(instance = instance)
