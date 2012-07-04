from django.db import models

class ConditionModel(models.Model):
	class Meta:
		app_label = 'vt_manager'

	condition = models.CharField(max_length = 512, default = "")
	ruletable = models.CharField(max_length = 512, default="")
