import os, string, hashlib, base64, ldap
from django.template import Context, loader
from django.core import mail
from django.conf import settings
from random import choice

def project_path(rel_path):
	"Helper method which joins the project's path with the rel_path specified "
	return os.path.join(os.path.dirname(os.path.abspath(__file__)), rel_path)

def make_safe_name(str):
	return ''.join([(i if (i in (string.ascii_letters+string.digits)) else '') for i in str.lower()])

def hash_password(password):
	return '{SHA}'+ base64.b64encode(hashlib.sha1(password).digest())

def generate_random_password(len=8, chars=string.letters+string.digits):
	return ''.join([choice(chars) for i in range(len)])
	
def send_mail(to_mail, subject, template_name, **args):
	"""
	Sends an email by rendering the template specified (in templates/mailer/...).
	The argument hash is passed to the template as context.
	"""
	template = loader.get_template("mailer/%s" % template_name)
	context = Context(args)
	body = template.render(context)
	mail.send_mail(subject, body, settings.MAIL_FROM, [to_mail], fail_silently=True)
	print 'Sending: "%s" to "%s"' % (subject, to_mail)
	print body

def ldap_connection():
	l = ldap.initialize(settings.LDAP_SERVER)
	l.simple_bind_s(settings.LDAP_USER, settings.LDAP_PASSWORD)
	return l

class LdapException(Exception):
	pass
