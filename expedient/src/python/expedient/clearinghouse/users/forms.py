'''
Created on Dec 3, 2009

@author: jnaous
'''

from django import forms
from models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm, PasswordResetForm
from registration.forms import RegistrationForm
from django.contrib.sites.models import Site
from django.template import Context, loader
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import int_to_base36


class UserProfileForm(forms.ModelForm):
    '''
    A form for editing UserProfiles
    '''
    
    class Meta:
        model = UserProfile
        exclude = ('user')

class UserForm(forms.ModelForm):
    '''
    A form for editing Users
    '''
    class Meta:
        model = User
        exclude = ('username', 'password', 'last_login',
                   'date_joined', 'groups', 'user_permissions',
                   'is_superuser', 'is_staff', 'is_active')

class FullRegistrationForm(RegistrationForm):
    first_name = forms.CharField(max_length=40)
    last_name = forms.CharField(max_length=40)
    affiliation = forms.CharField(
        max_length=100,
        help_text="The organization that you are affiliated with.")

    '''
    A minimal exception control is implemented to avoid users registered
    at the database with only their basic info (defined in RegistrationForm's
    model) and no activation e-mail being sent to them.
    '''    
    def save(self, profile_callback=None):
	try:
                user = super(FullRegistrationForm, self).save(
                    profile_callback=profile_callback)
                user.first_name = self.cleaned_data["first_name"]
                user.last_name = self.cleaned_data["last_name"]
                user.save()
                UserProfile.objects.create(
                    user=user, affiliation=self.cleaned_data["affiliation"])
        except Exception as e:
            # If user could not be registered, try to delete it
            try:
                failed_user = User.objects.get(username=self.data['username'])
                failed_user.delete()
            # If some error happens, user may have not been even saved to database. Ignore
            except:
                pass
            raise e
        return user

class AdminPasswordChangeFormDisabled(AdminPasswordChangeForm):
    '''
    A form used to change the password of a user in the admin interface, with
    the password fields shown disabled initially.
    '''
    
    def __init__(self, *args, **kwargs):
        super(AdminPasswordChangeFormDisabled, self).__init__(*args, **kwargs)
        for field in ['password1', 'password2']:
            self.fields[field].widget.attrs['disabled'] = True

class PasswordChangeFormDisabled(PasswordChangeForm):
    '''
    A form used to change the password of a user, with
    the password fields shown disabled initially. Requires confirmation
    with the old password
    '''
    
    def __init__(self, *args, **kwargs):
        super(PasswordChangeFormDisabled, self).__init__(*args, **kwargs)
        for field in ['old_password', 'new_password1', 'new_password2']:
            self.fields[field].widget.attrs['disabled'] = True

class LDAPPasswordResetForm(PasswordResetForm):

    def save(self, domain_override=None, email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator):
        """
        Generates a one-use only link for resetting password and sends to the user.
        A minimal exception control is implemented to avoid problems with e-mail.
        """
        from expedient.common.utils.mail import send_mail # Wrapper for django.core.mail__send_mail
        for user in self.users_cache:
            if not domain_override:
                current_site = Site.objects.get_current()
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            if user.password == '!':
                t = loader.get_template('registration/password_reset_email_ofreg.html')
            else:
                t = loader.get_template(email_template_name)
            c = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': int_to_base36(user.id),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': use_https and 'https' or 'http',
            }
            try:
                send_mail(("Password reset for user %s in %s") % (user.username,site_name),
                    t.render(Context(c)), None, [user.email])
            except Exception as e:
                print "[ERROR] Exception at 'expedient.clearinghouse.users.forms': user '%s' (%s) could not fully reset its password. LDAPPasswordResetForm returned: %s" % (user.username, user.email, str(e))
