'''
Created on Jun 17, 2010

@author: jnaous
'''
from django import forms
from expedient.clearinghouse.project.models import Project
from django.contrib.auth.models import User
from expedient.clearinghouse.roles.models import ProjectRole
from expedient.common.permissions.models import Permittee
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape

class ProjectCreateForm(forms.ModelForm):
    """
    Form to create a project with basic information.
    """
    class Meta:
        model = Project

class RoleModelChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return mark_safe("<span class='val role_desc'>%s</span>" \
            "<span class='description role_desc'>%s</span>" % (
                conditional_escape(obj.name),
                conditional_escape(obj.description)
            )
        )

class AddMemberForm(forms.Form):
    """Form to add a member to a project
    
    Has fields to select a form and select roles.
    
    @ivar user: C{django.forms.ModelChoiceField} to select a user
    @ivar roles: C{django.forms.ModelMultipleChoiceField} to select roles
    @ivar delegate: C{django.forms.BooleanField} should the new member be
        able to give the roles/permissions she has to others?
    """
    
    user = forms.ModelChoiceField(
        User.objects.all(), help_text="Select the new user to add to the project.")
    roles = RoleModelChoiceField(
        ProjectRole.objects.all(), widget=forms.CheckboxSelectMultiple,
        help_text="Select the roles that the user should have in this project."
    )
    delegate = forms.BooleanField(required=False,
        help_text="Should the new member be able to give the new permissions"
        " and roles to others?")
    
    def __init__(self, project, giver, *args, **kwargs):
        if not isinstance(project, Project):
            raise Exception(
                "Expected %s instance as first argument. "
                "Got a %s instead." % (Project, project.__class__)
            )

        super(AddMemberForm, self).__init__(*args, **kwargs)
        
        self.fields["user"].queryset = User.objects.exclude(
            id__in=list(project.members.values_list("id", flat=True)))
        
        self.fields["roles"].queryset = \
            ProjectRole.objects.filter_for_can_delegate(
                giver).filter(project=project)
        
        self.project = project
        self.giver = giver
                
    def save(self):
        user = self.cleaned_data["user"]
        roles = self.cleaned_data["roles"]
        delegate = self.cleaned_data["delegate"]
        
        for role in roles:
            role.give_to_permittee(
                user, giver=self.giver, can_delegate=delegate)
        
        
class MemberForm(forms.Form):
    """Form to set roles for a member in the project
    
    @ivar roles: C{django.forms.ModelMultipleChoiceField} to select roles
    """
    
    roles = RoleModelChoiceField(
        ProjectRole.objects.all(), widget=forms.CheckboxSelectMultiple,
        help_text="Select the roles that the user should have in this project."
    )
    delegate = forms.BooleanField(required=False,
        help_text="Should the member be able to give the permissions"
        " and roles to others?")
    
    def __init__(self, project, user, giver, *args, **kwargs):
        if not isinstance(project, Project):
            raise Exception(
                "Expected %s instance as first argument. "
                "Got a %s instead." % (Project, project.__class__)
            )
        if not isinstance(user, User):
            raise Exception(
                "Expected %s instance as second argument. "
                "Got a %s instead." % (User, user.__class__)
            )
        if not isinstance(giver, User):
            raise Exception(
                "Expected %s instance as third argument. "
                "Got a %s instead." % (User, giver.__class__)
            )

        super(MemberForm, self).__init__(*args, **kwargs)
        
        self.fields["roles"].queryset = \
            ProjectRole.objects.filter_for_can_delegate(
                giver).filter(project=project)
    
        permittee = Permittee.objects.get_as_permittee(user)
    
        self.initial_roles = permittee.projectrole_set.filter(project=project)
    
        self.fields["roles"].initial = list(
            self.initial_roles.values_list('pk', flat=True))
        
        self.user = user
        self.giver = giver
        
    def save(self):
        for r in self.cleaned_data["roles"]:
            r.give_to_permittee(
                self.user,
                giver=self.giver,
                can_delegate=self.cleaned_data["delegate"])
        
        for role in self.initial_roles:
            if role not in self.cleaned_data["roles"]:
                role.remove_from_permittee(self.user)
