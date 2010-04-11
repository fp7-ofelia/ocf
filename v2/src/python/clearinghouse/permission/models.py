from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User

class SecureObjects(models.Model):
    content_type = models.ForeignKey(ContentType, editable=False, 
                                     null=True, blank=True)
    object_id = models.PositiveIntegerField(editable=False,
                                            null=True, blank=True)
    content_object = generic.GenericForeignKey()

    field_name = models.CharField(max_length=200, default="")
    
class UserRule(models.Model):
    user = models.ForeignKey(User)
    def rule(self):
        ret = []
        ret.extend(User.objects.filter(projects__in=self.user.projects.all()).all())
    
class Category(models.Model):
    rules = models.ManyToManyField(Rule)
    name = models.CharField(max_length=100)
