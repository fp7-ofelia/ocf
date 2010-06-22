'''
Created on Jun 17, 2010

@author: jnaous
'''
from django import forms
from expedient.clearinghouse.project.models import Project

class ProjectCreateForm(forms.ModelForm):
    """
    Form to create a project with basic information.
    """
    class Meta:
        exclude = ["owner", "aggregates"]
        model = Project
