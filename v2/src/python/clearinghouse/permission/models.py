from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User

import cPickle as pickle

class PickledObjectField(models.TextField):
    def to_python(self, value):
        return pickle.loads(value)
    
    def get_db_prep_value(self, value):
        return pickle.dumps(value)

class SecureObjects(models.Model):
    content_type = models.ForeignKey(ContentType, editable=False, 
                                     null=True, blank=True)
    object_id = models.PositiveIntegerField(editable=False,
                                            null=True, blank=True)
    content_object = generic.GenericForeignKey()

    field_name = models.CharField(max_length=200, default="")

class FilterParam(models.Model):
    name = models.CharField(max_length=50, default="")
    key = models.CharField(max_length=200)
    val = PickledObjectField()
    
    def get_as_dict(self, instance):
        if callable(self.val):
            val = self.val(instance)
        return {self.key: val}

class FieldName(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
class Rule(models.Model):
    name = models.CharField(max_length=50, default="")
    content_type = models.ForeignKey(ContentType, editable=False)
    filter_params = models.ManyToManyField(FilterParam)
    exclude_params = models.ManyToManyField(FilterParam)
    filter_first = models.BooleanField("Apply the filtering rule first?",
                                       default=True)
    field_names = models.ManyToMany(FieldName)
    
    def get_model_instances(self, instance):
        filters = {}
        excludes = {}
        for f in self.filter_params.all():
            filters.update(f.get_as_dict(instance))
        for f in self.exclude_params.all():
            excludes.update(f.get_as_dict(instance))

        if self.filter_first:
            return self.content_type.filter(**filters).exclude(**excludes)
        else:
            return self.content_type.exclude(**excludes).filter(**filters)
    
class Category(models.Model):
    from_rules = models.ManyToManyField(Rule)
    to_rules = models.ManyToManyField(Rule)

create_category(
    name="user_email_to_teammates",
    default=True,
    secrecy=True,
    owner=User,
    elements=[
        User.email,
        lambda user: User.objects.filter(project__in=user.projects.all()),
    ],
)
create_category(
    name="user_email_from_user",
    default=True,
    integrity=True,
    owner=User,
    elements=[
        User.email,
        lambda user: [user],
    ],
)
create_category(
    name="project_info",
    secrecy_rules={
        # only members can see the list of members
        Project.members: lambda inst:User.objects.filter(project=inst).all()
    },
    integrity_rules={
        Project.members: lambda inst:User.objects.filter(project=inst, permission=inst.add_member_permission).all()
    }
)

email = FieldName.objects.get_or_create(name="email")
email_from_rule = Rule.objects.create(
    name="user_email_from_rule",
    content_type=ContentType.objects.get_for_model(User),
    field_names=[email],
)
to_teammates_rule = Rule.objects.create(
    name="to_teammates_rule",
    content_type=ContentType.objects.get_for_model(User),
)
project_teammates = FilterParam(
    name="project_teammates",
    key="project_in",
    val=lambda inst: inst.project_set.all(),
)
email_category = Category.objects.create (
    from_rules=[email_from_rule],
    to_rules=[to_teammates_rule],
)

def get_modified_fields(model, curr_obj):
    # get the old object from the db
    try:
        old_obj = model.objects.get(pk=curr_obj.pk)
    except model.DoesNotExist:
        # The object is not in the database to begin with.
        return curr_obj
    
    return [
        f.attname \
        for f in old_obj._meta.fields \
        if getattr(old_obj, f.attname) != getattr(curr_obj, f.attname)
    ]
 
def check_save(sender, **kwargs):
    changed_fields = get_modified_fields(sender, kwargs['instance'])
    if changed_fields == kwargs['instance']:
        # new entry
        return
    else:
        # for each category read, check that the fields written are in the
        # to_fields.
        # for each field written, check that the categories read are
        # allowed to modify the written fields
        pass

