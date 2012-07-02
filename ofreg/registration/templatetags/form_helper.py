from django import template
from django.utils.safestring import *

register = template.Library()

@register.simple_tag
def field_row(form, field_name, after_html=""):
	field = form[field_name]
	errors = field.errors.as_text()
	if errors:
		errors = "<span class=\"error\">%s</span>" % errors
	res = "<div>%(label)s %(field)s %(after)s %(errors)s</div>" % { 
		'label'  : field.label_tag(), 
		'field'  : field,
		'errors' : errors,
		'after'  : after_html}
	return mark_safe(res)

@register.simple_tag
def submit_row(label):
	return mark_safe("<div><input type=\"submit\" value=\"%s\" class=\"submit\"></div>" % label)
