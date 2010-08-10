'''
Created on Aug 10, 2010

@author: jnaous
'''
from django import forms
from django.contrib.auth.models import User
from expedient.clearinghouse.roles.models import ProjectRoleRequest

class SelectRoleForm(forms.ModelForm):
    class Meta:
        model = ProjectRoleRequest
        fields = ['requested_role', 'giver', 'message']

    def __init__(self, roles_qs, roles_to_users, *args, **kwargs):
        '''
        @param roles_qs: queryset of allowed roles
        @param roles_to_users: dict mapping each role in roles_qs to a
            set of users
        '''
        super(SelectRoleForm, self).__init__(*args, **kwargs)
        self.fields["requested_role"].queryset = roles_qs
        ids = []
        for users in roles_to_users.values():
            ids.extend(list(users.values_list("pk", flat=True)))
        self.fields["giver"].queryset = User.objects.filter(pk__in=ids)
        self.roles_to_users = roles_to_users
        
    def clean(self):
        
        user = self.cleaned_data.get("giver")
        role = self.cleaned_data.get("requested_role")
        
        if user and role:
            # check that the user is valid for the role
            users_qs = self.roles_to_users[role.id]
            
            if user not in users_qs:
                raise forms.ValidationError(
                    "Chosen role cannot be given by chosen user.")
    
        return self.cleaned_data