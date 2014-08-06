'''
Created on Aug 10, 2010

@author: jnaous
'''
from itertools import chain
from django import forms
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from expedient.clearinghouse.roles.models import ProjectRoleRequest, \
    ProjectRole
from expedient.common.permissions.models import ObjectPermission
from django.forms.widgets import CheckboxSelectMultiple, CheckboxInput
from django.utils.encoding import force_unicode
from expedient.common.permissions.shortcuts import has_permission
from expedient.common.middleware import threadlocals

class RoleModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return mark_safe(u"<span class='val role_desc'>%s</span>" \
            u"<span class='description role_desc'>%s</span>" % (
                conditional_escape(obj.name),
                conditional_escape(obj.description)
            )
        )

class PermissionModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        name = u"<div class='val perm_desc'>%s</div>" \
        u"<div class='description perm_desc'>%s</div>" % (
            conditional_escape(obj.permission.name),
            conditional_escape(obj.permission.description),
        )
        target = conditional_escape(u"%s" % obj.target)
        
        return mark_safe(u"<td>%s</td><td>%s</td>" % (name, target))

class PermissionCheckboxTableSelectMultiple(CheckboxSelectMultiple):
    """A C{CheckboxSelectMultiple} widget that renders as a table instead of list"""
    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<table class="permission_checkbox_table formtable_noborder">']
        output.append(u'    <tr>')
        output.append(u'        <th></th>')
        output.append(u'        <th>Name</th>')
        output.append(u'        <th>Target</th>')
        output.append(u'    </tr>')
        
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        # Original code: multiple permissions were being shown
#        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
        for i, (option_value, option_label) in enumerate(chain(set(chain(self.choices, choices)))):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                row_id = u' "row_%s"' % final_attrs['id']
            else:
                row_id = ''

            cb = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(u'    <tr id=%s>' % row_id)
            output.append(u'        <td>%s</td>' % rendered_cb)
            output.append(u'        %s' % option_label)
            output.append(u'    </tr>')
        output.append(u'</table>')
        return mark_safe(u'\n'.join(output))

class SelectRoleForm(forms.ModelForm):
    """Form to select a role and a giver to create a ProjectRoleRequest"""
    
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
    
class ProjectRoleForm(forms.ModelForm):
    """Form to create/update ProjectRole instances"""
    
    obj_permissions = PermissionModelMultipleChoiceField(
        ObjectPermission.objects.get_empty_query_set(),
        label="Role's permissions",
        help_text=\
            "Select the permissions that users who have role should have.",
        widget=PermissionCheckboxTableSelectMultiple,
    )
    
    class Meta:
        model = ProjectRole
        exclude = ["project", "permittees"]
        
    def __init__(self, *args, **kwargs):
        self.obj_permissions = kwargs.pop(
            "obj_permissions", ObjectPermission.objects.get_empty_query_set())
        self.user = kwargs.pop(
            "user", threadlocals.get_thread_locals()["user"])
        super(ProjectRoleForm, self).__init__(*args, **kwargs)
        self.fields["obj_permissions"].queryset = self.obj_permissions
        
    def clean_obj_permissions(self):

        new_obj_permissions = self.cleaned_data["obj_permissions"]
        new_obj_permissions_pks = [p.pk for p in new_obj_permissions]
        initial_role_pks = self.fields["obj_permissions"].initial

        if not initial_role_pks:
            return new_obj_permissions
 
        for perm_pk in initial_role_pks:
            if perm_pk not in new_obj_permissions_pks and\
            not has_permission(self.user, self.project, "can_remove_members"):
                perm = ObjectPermission.objects.get(pk=perm_pk)
                raise forms.ValidationError(
                    "You tried to remove permission '%s' for target '%s' "
                    "from the role, "
                    "but you do not have permission to remove members "
                    "so you cannot remove permissions from roles either."
                    % (perm.permission.name, perm.target))

        return new_obj_permissions

    def save(self, commit = False):
        """
        Update instance with the new checked permissions.
        """
        instance = super(ProjectRoleForm, self).save(commit=False)
        # ProjectRole may have not been committed yet, lacking therefore of PK
        # If that is the case, do not try to add the object permissions in the
        # same way this is done for the update
        try:
            instance.obj_permissions = self.cleaned_data["obj_permissions"]
        except:
            pass
        if commit:
            instance.save()
        return instance

