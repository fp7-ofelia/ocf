from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from clearinghouse.middleware import threadlocals

class Policy(object):
    def __init__(self, model, fields, readers, writers):
        self.model = model;
        self.fields = fields;
        self.readers = readers;
        self.writers = writers;
        
        
def check_save(sender, **kwargs):
    '''
    make sure that the modified fields are writeable by the user and the url.
    '''
    
    changed_fields = get_changed_fields(sender, kwargs['instance'])
    user = threadlocals.get_current_user()
    (url_name, url_params) = threadlocals.get_request_url()
    
    for field in changed_fields:
        rule = get_user_rule(sender, field)
        if user not in rule.can_write(user, kwargs['instance']):
            raise Exception("User %s cannot write field %s of %s" % ())
        rule = get_url_rule(url_name, url_params)
        if not rule.can_write(kwargs['instance'], field):
            raise Exception("View for URL %s tried to write outside its "
                + "declared fields: instance %s, field %s." %(
                    kwargs['instance'], field))

# TODO: Filter the readable objects so that we only return objects that:
# a) are readable by the current user
# b) are readable by a subset of the users as the objects that will be written by the function.
