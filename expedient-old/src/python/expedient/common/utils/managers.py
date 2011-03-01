'''
Created on Jun 19, 2010

@author: jnaous
'''
from django.db import models
from django.contrib.contenttypes.models import ContentType

class GenericObjectManager(models.Manager):
    """
    Adds methods to retrieve generic objects when the model uses the
    contenttypes framework.
    
    @keyword ct_field: name of the ForeignKey field pointing to C{ContentType}.
        Default is "content_type".
    @keyword fk_field: name of the ID field for objects. Default is
        C{object_id}.
    """
    
    use_for_related_fields = True
    
    def __init__(self, ct_field="content_type", fk_field="object_id"):
        super(GenericObjectManager, self).__init__()
        self.ct_field = ct_field
        self.fk_field = fk_field
        
    def get_or_create_from_instance(self, instance, **kwargs):
        """
        Similar to the C{get_or_create} method, but accepts an instance
        object to be used for the generic foreign key relation.
        """
        kwargs.update({
            self.ct_field: ContentType.objects.get_for_model(instance),
            self.fk_field: instance.id,
        })
        return self.get_or_create(**kwargs)
    
    def filter_from_instance(self, instance):
        """
        Get the generic objects pointing to the instance.
        
        @param instance: instance to retrieve the object for.

        @return: C{QuerySet} containing all generic object.
        """
        return self.filter(**{
            self.ct_field: ContentType.objects.get_for_model(instance),
            self.fk_field: instance.id,
        })
        
    def filter_from_queryset(self, queryset):
        """
        Get a filtered queryset that contains all the objects for all instances
        in queryset. This will only return a query set of the objects found.
        Some may not exist.
        
        @param queryset: QuerySet of objects whose generic counterparts we wish
            to find.
            
        @return: C{QuerySet} that contains the generic objects.
        """
        return self.filter(**{
            self.ct_field: ContentType.objects.get_for_model(queryset.model),
            self.fk_field + "__in": queryset.values_list("pk", flat=True),
        })
        
    def filter_for_class(self, klass, **kwargs):
        """
        Convenience function to filter for generic objects related to a
        particular class. Accepts same arguments as the normal C{filter()}
        method.
        
        @param klass: Class to filter by.
        """
        
        f = {self.ct_field: ContentType.objects.get_for_model(klass)}
        f.update(kwargs)
        return self.filter(**f)
    
    def get_objects_queryset(self, klass, generic_filter_args,
                             object_filter_args):
        """
        Convenience function to filter both the generic objects and the objects
        they point to, and return a queryset for the class C{klass}.
        """
        obj_ids = self.filter_for_class(
            klass, **generic_filter_args).values_list(self.fk_field, flat=True)
        return klass.objects.filter(pk__in=obj_ids, **object_filter_args)
        
    def filter_for_objects(self, klass, **object_filter_args):
        """
        Filter the generic objects to return the queryset that contains
        objects of class C{klass} filtered by the rest of the keywords.
        """
        ct = ContentType.objects.get_for_model(klass)
        obj_ids = klass.objects.filter(
            **object_filter_args).values_list("pk", flat=True)
        return self.filter(**{self.ct_field: ct,
                              "%s__in" % self.fk_field: obj_ids})
