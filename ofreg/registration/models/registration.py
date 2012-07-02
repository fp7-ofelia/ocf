import uuid
import ldap
import httplib, urllib

from django import forms
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from ofreg import util

# from form import Form

class Registration(models.Model):
	name            = models.CharField(max_length=255)
	email           = models.EmailField()
	password        = models.CharField(max_length=255)
	organization    = models.CharField(max_length=255)
	island          = models.CharField(max_length=255, choices=settings.OFELIA_ISLANDS, verbose_name="Home Island")
	public_key      = models.TextField()
	validation_hash = models.CharField(max_length=255, blank=True)

	def _get_safe_name(self):
		return util.make_safe_name(self.name)
	
	safe_name = property(_get_safe_name)

	class Meta:
		app_label="registration"

	class LdapException(Exception):
		pass

	# Set validation_hash
	# Can be done via pre-save call back as well
	def save(self, *args, **kwargs):
		self.validation_hash = str(uuid.uuid4())
		super(Registration, self).save(*args, **kwargs)
	
	# Validate that user name is unique in LDAP and is not in blocked users
	def clean(self):
		super(Registration, self).clean()
		# is user in BLOCKED_USERS
		if self.safe_name in settings.BLOCKED_USERNAMES:
			raise ValidationError('Name (%s) can not be chosen, please choose another name' % self.safe_name)
			
		# user in LDAP already?
		l = util.ldap_connection()
		res = l.search_s(settings.LDAP_USERGP, ldap.SCOPE_SUBTREE, '(cn=%s)' % self.safe_name, [])
		l.unbind_s()
		if len(res) > 0:
			raise ValidationError('Name (%s) already exists in LDAP, please choose another name' % self.safe_name)

	def transfer_to_ldap(self):
		# calculate data needed
		try:
			protocol = '' # protocol for logging what is happing
			# initialization & authentication
			protocol += 'initialize & bind; '
			l = util.ldap_connection()
			# add to LDAP
			ldap_data = self.as_ldap()
			protocol += "add user %s; " % self.safe_name
			l.add_s('cn=%s,%s' % (self.safe_name, settings.LDAP_USERGP), ldap_data['user']) # add user
			protocol += 'add automount; '
			l.add_s('cn=%s,%s' % (self.safe_name, settings.LDAP_MOUNTGP), ldap_data['automount']) # add mount info
			protocol += 'add to expedient ACL; '
			l.modify_s(settings.LDAP_EXPEDIENTGP, ldap_data['expedient']) # add expedient access

			protocol += 'query VPN group; '
			old_vpn = l.search_s(settings.LDAP_VPNGP, ldap.SCOPE_SUBTREE, "(cn=%s)" % (settings.LDAP_VPNCN), [])
			protocol += "(cn=%s)" % (settings.LDAP_VPNCN)
			protocol += "  " + "cn=%s,%s" % (settings.LDAP_VPNCN, settings.LDAP_VPNGP)
			new_vpn = []
			new_vpn.append( ('objectClass', old_vpn[0][1]['objectClass']) )
			new_vpn.append( ('cn', old_vpn[0][1]['cn']) )
			new_vpn.append( ('nisNetgroupTriple', old_vpn[0][1]['nisNetgroupTriple'] + [str("(,%s,)" % self.safe_name)]) )
			protocol += 'delete VPN group; '
			l.delete_s("cn=%s,%s" % (settings.LDAP_VPNCN, settings.LDAP_VPNGP))
			protocol += 'add modified VPN group; '
			l.add_s(("cn=%s,%s" % (settings.LDAP_VPNCN, settings.LDAP_VPNGP)), new_vpn)
			# release binding
			protocol += 'release binding; '
			l.unbind_s()
		except ldap.LDAPError, e:
			raise Registration.LdapException("%s: %s" % (e, protocol)) #[0]['desc'])
		
		# finally delete the entry if transfer to LDAP went well
		self.delete()

	def as_ldap(self):
		"""
		Returns a hash with LDAP entries for using with ldap.add(...) / ldap.modify(...):
		{
		  'user'      : ... # used for putting into the user section (add)
		  'automount' : ... # used for putting into the automount section (add)
		  'exedient' : ... # used for changing the expedient ACL (modify)
		}
		"""
		uid = settings.LDAP_UID_START + self.id
		gid = settings.LDAP_GID_START + self.id
		info_dict = { 'safe_name' : self.safe_name, 'uid' : uid, 'gid' : gid, 'island' : self.island } # used for string replacements
		home = settings.LDAP_HOME % info_dict
		mount_info = settings.LDAP_MOUNT_INFO % info_dict
		password = util.hash_password(self.password)

		return {
		  'user' : [
			('objectClass', ['top', 'posixAccount', 'inetOrgPerson', 'ldapPublicKey']),
			('uid', str(self.safe_name)),
			('sn', str(self.safe_name)),
			('uidNumber', str(uid)),
			('gidNumber', str(gid)),
			('homeDirectory', str(home)),
			('givenName', str(self.name)),
			('o', str(self.organization)),
			('mail', str(self.email)),
			('userPassword', str(password)),
			('loginShell', str(settings.LDAP_LOGIN_SHELL)),
			('sshPublicKey', str(self.public_key)),
			('description', str(self.island))],
		  'automount' : [
			('objectClass', 'automount'),
			('automountInformation', str(mount_info))],
		  'expedient' : [
			(ldap.MOD_ADD, 'uniqueMember', str("uid=%s,%s" % (self.safe_name, settings.LDAP_USERGP)))]
		}

class RegistrationForm(forms.ModelForm):
	password = forms.CharField(max_length=255, widget=forms.PasswordInput)
	password_confirmation = forms.CharField(max_length=255, widget=forms.PasswordInput)
	usage_accept    = forms.BooleanField(required=True, label="I accept the usage policy")

	recaptcha_challenge_field = forms.CharField(max_length=255, widget=None)
	recaptcha_response_field = forms.CharField(max_length=255, widget=None)
	recaptcha_remote_ip = None

	def clean_password_confirmation(self):
		cleaned_data = self.cleaned_data
		if cleaned_data.get('password') != cleaned_data.get('password_confirmation'):
			raise ValidationError('Password confirmation did not match.')
	
	def clean(self):
		super(RegistrationForm, self).clean()
		# reCaptcha correct?
		headers = {
			"Content-type" : "application/x-www-form-urlencoded",
		    "Accept"       : "text/plain"}
		params = urllib.urlencode({
			'privatekey': '6LdJ6MYSAAAAACfc7E6tgpHVGzR0qfi8fD7q_9vU', 
			'remoteip'  : self.recaptcha_remote_ip, 
			'challenge' : self.cleaned_data['recaptcha_challenge_field'],
			'response'  : self.cleaned_data.get('recaptcha_response_field', '')})
		conn = httplib.HTTPConnection("www.google.com")
		conn.request("POST", "/recaptcha/api/verify", params, headers)
		capcha_response = conn.getresponse()

		if capcha_response.status == 200:
			data = capcha_response.read()
		else:
			data = ''
		conn.close()
		capcha_ok = data.startswith('true')
		if not capcha_ok: # captcha wrong (or another error)
			raise ValidationError('Please enter the Captcha correctly')
			# bits = data.split('\n', 2)
			# error_code = ''
			# if len(bits) > 1:
			# 	error_code = bits[1]
			# raise Exception(error_code)
		return self.cleaned_data
	
	class Meta:
		model = Registration
