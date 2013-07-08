'''
Created on Jun 17, 2010

@author: jnaous
'''
from django import forms
from expedient.clearinghouse.project.models import Project
from django.contrib.auth.models import User
from expedient.clearinghouse.roles.models import ProjectRole
from expedient.common.permissions.models import Permittee
from expedient.common.permissions.shortcuts import has_permission
from expedient.clearinghouse.roles.forms import RoleModelMultipleChoiceField

class ProjectCreateForm(forms.ModelForm):
    """
    Form to create a project with basic information.
    """
    class Meta:
        model = Project

class AddMemberForm(forms.Form):
    """Form to add a member to a project
    
    Has fields to select a form and select roles.
    
    @ivar user: C{django.forms.ModelChoiceField} to select a user
    @ivar roles: C{django.forms.ModelMultipleChoiceField} to select roles
    @ivar delegate: C{django.forms.BooleanField} should the new member be
        able to give the roles/permissions she has to others?
    """
    
    user = forms.ModelChoiceField(
        User.objects.get_empty_query_set(),
        help_text="Select the new user to add to the project.")
    roles = RoleModelMultipleChoiceField(
        ProjectRole.objects.get_empty_query_set(),
        widget=forms.CheckboxSelectMultiple,
        help_text="Select the roles that the user should have in this project. Owner users can add memebers to the project, researchers can not."
    )
    #delegate = forms.BooleanField(required=False,
    #    help_text="Should the new member be able to give the new permissions"
    #    " and roles to others?")
    
    def __init__(self, project, giver, *args, **kwargs):
        if not isinstance(project, Project):
            raise Exception(
                "Expected %s instance as first argument. "
                "Got a %s instead." % (Project, project.__class__)
            )

        super(AddMemberForm, self).__init__(*args, **kwargs)
        
        self.fields["user"].queryset = User.objects.exclude(
            id__in=list(project.members.values_list("id", flat=True))).order_by('username')
        
        if giver.is_superuser:
            self.fields["roles"].queryset = \
                ProjectRole.objects.filter(project=project).order_by('name')
        else:
            self.fields["roles"].queryset = \
                ProjectRole.objects.filter_for_can_delegate(
                    giver, project=project).order_by('name')
        
        self.project = project
        self.giver = giver
                
    def save(self):
        user = self.cleaned_data["user"]
        roles = self.cleaned_data["roles"]
        #delegate = self.cleaned_data["delegate"]
        
        for role in roles:
            if role.name == "owner":
                delegate = True
            else:
                delegate = False

            role.give_to_permittee(
                user, giver=self.giver, can_delegate=delegate)
        
        
class MemberForm(forms.Form):
    """Form to set roles for a member in the project
    
    @ivar roles: C{django.forms.ModelMultipleChoiceField} to select roles
    """
    
    roles = RoleModelMultipleChoiceField(
        ProjectRole.objects.all().order_by('name'), widget=forms.CheckboxSelectMultiple,
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
        
#        self.fields["roles"].queryset = \
#            ProjectRole.objects.filter_for_can_delegate(
#                giver, project=project)

        # Allow not only the giver but everyone with 'can_edit_roles'
        # permission to update other's roles
        self.fields["roles"].queryset = ProjectRole.objects.filter(project=project)
    
        permittee = Permittee.objects.get_as_permittee(user)
    
        self.initial_roles = permittee.projectrole_set.filter(project=project)
    
        self.fields["roles"].initial = list(
            self.initial_roles.values_list('pk', flat=True))
        
        self.user = user
        self.giver = giver
        self.project = project
        
    def clean_roles(self):
        """
        Make sure that no roles have been taken out unless the
        user has the "can_remove_members" permission.
        """
        roles = self.cleaned_data["roles"]
        for role in self.initial_roles:
            if role not in roles and\
            not has_permission(self.giver, self.project, "can_remove_members"):
                raise forms.ValidationError(
                    "You tried to remove role '%s' from the user, "
                    "but you do not have permission to remove members "
                    "so you cannot remove roles from members either." % role.name)
            
        return roles
        
    def save(self):
        for r in self.cleaned_data["roles"]:
            r.give_to_permittee(
                self.user,
                giver=self.giver,
                can_delegate=self.cleaned_data["delegate"])
        
        for role in self.initial_roles:
            if role not in self.cleaned_data["roles"]:
                role.remove_from_permittee(self.user)
