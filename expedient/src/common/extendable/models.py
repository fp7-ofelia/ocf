'''
@author: jnaous
'''
import logging
from django.db import models
from django.db.models.base import ModelBase
from django.utils.importlib import import_module
from expedient.common.tests.utils import drop_to_shell

logger = logging.getLogger("extendable.models")

class ExtendableMeta(ModelBase):
    '''
    Metaclass for all Extendable models.
    '''
    
    def __new__(cls, name, bases, attrs):
        '''Add the fields in 'extended_fields to all 
        grandchildren of Extendable. Also connect the post_save signal
        to save the content_object.'''
        
        # get the inner Extend class
        class Extend: pass
        extend = attrs.setdefault('Extend', Extend)

        # Only do this for subclasses of Extendable
        if (name != "Extendable" or
        attrs['__module__'] != ExtendableMeta.__module__):

            # get the extended fields of the parents
            extended_fields = {}
            repl_kw = set()
            for base in bases:
                if isinstance(base, ExtendableMeta):
                    base_extend = getattr(base, "Extend", Extend)
                    # check for clashes in field names and replacement keywords
                    # and add to dict
                    for fname, fval in \
                    getattr(base_extend, "fields", {}).items():
                        field_cls, args, kwargs, args_repl, kwargs_repl = fval
                        if fname in extended_fields:
                            raise Exception(
                                "Extended field '%s' from %s " % (fname, base)
                                +"already defined in another parent of "
                                +"%s.%s" % (attrs['__module__'], name))
                        else:
                            clashes = set(args_repl).intersection(repl_kw)
                            clashes = clashes.union(set(kwargs_repl.values())\
                                .intersection(repl_kw))
                            if clashes:
                                raise Exception(
                                    "Replacement keywords '%s' " % clashes
                                    +"from %s already " % attrs['__module__']
                                    +"defined in another parent of %s.%s" % (
                                        name, base))
                            else:
                                extended_fields[fname] = fval
            
            # get the delegations, check that they are all in extended_fields
            delegations = getattr(extend, "redelegate", [])
            for d in delegations:
                if d not in extended_fields:
                    raise Exception(
                        "Redelegated field '%s' is not an extended" % d
                        +" field in any of %s.%s's parents." %(
                            attrs['__module__'], name))
                else:
                    # remove the field from the list to add to this class
                    # and put it in this class's inner Extend
                    extend.fields = getattr(extend, "fields", {})
                    extend.fields[d] = extended_fields[d]
                    del extended_fields[d]
            
            if extended_fields:
                # get replacements
                repl = getattr(extend, 'replacements', {})
                
                # create each field in the child, replacing when necessary
                for fname, fval in extended_fields.items():
                    # expand the information about the field
                    field_cls, args, kwargs, args_repl, kwargs_repl = fval

                    # check if there are any replacement for arguments
                    if args_repl:
                        if len(args_repl) != len(args):
                            raise Exception("Arguments list must be of the "
                                            + "same length as its replacement "
                                            + "keywords.")
                        z = zip(args, args_repl)
                        args = [repl[t[1]] \
                                if t[1] != None and t[1] in repl \
                                else t[0] for t in z]
                        
                    # check for keyword argument replacements
                    kwargs = kwargs.copy()
                    if kwargs_repl:
                        for repl_arg, repl_key in kwargs_repl.items():
                            if repl_key in repl:
                                kwargs[repl_arg] = repl[repl_key]
                    
                    # check for clashes
                    if fname in attrs:
                        raise Exception(
                            "Field '%s' clashes with extended field " % fname
                            +"in class %s.%s" % (attrs['__module__'], name))
                    
                    # now create the field in this class
                    attrs[fname] = field_cls(*args, **kwargs)
                
        new_cls = super(ExtendableMeta, cls).__new__(cls, name, bases, attrs)
        
        return new_cls
    

class ExtendableManager(models.Manager):
    """
    A manager for Extendable objects.
    """

    def filter_for_class(self, klass):
        """
        Return a filtered QuerySet that only has instances whose
        leaf class is C{klass}.
        
        @param klass: The leaf model class of instances we are looking for.
        @type klass: a class
        """
        return self.filter(leaf_name=klass.__name__.lower())
    
    def filter_for_classes(self, klasses):
        """
        Return a filtered QuerySet that only has instances whose
        leaf class are in the list C{klasses}.
        
        @param klasses: List of leaf model classes of instances we are
            looking for.
        @type klasses: list of classes
        """
        cls_names = [c.__name__.lower() for c in klasses]
        return self.filter(leaf_name__in=cls_names)

class Extendable(models.Model):
    '''
    Extendable object.
    
    An extendable object that enables an instance to be obtained as its
    class's farthest descendant.
    
    Additionally, fields can be defined that would be added only
    to a direct subclass. This can be useful to automatically add relationships
    to subclasses so that relationships exist in the subclasses but not in the
    parents, allowing the same field name to be used for different types of
    relationships.
    
    Further, the class that inherits from C{Extendable} may specify which
    field initialization arguments 
    subclasses may override. Subclasses can override the arguments by adding
    values to a L{dict} in an inner class.
    
    Adding fields is done by adding an C{Extend} inner class. Three fields can
    be used in the C{Extend} inner class:
        1. C{fields}: This is a L{dict} that describes what the fields to be added
            in the subclass are. The format is as follows ::
            
            {field_name : (field_class, args, kwargs, repl_args, repl_kwargs)}
            
                - C{field_name}: name of the field to add to subclass
                - C{field_class}: class of the field e.g. ManyToManyField
                - C{args}: a list of pos args with which to init field_class
                - C{kwargs}: a list of keyword args with which to init field_class
                - C{repl_args}: either None or a list with the same length as 
                    C{args} that specifies which arguments can be overridden, and
                    what keyword to use to replace that argument.
                - C{repl_kwargs}: either None or a dict that specifies which kwargs
                    can be overridden by subclasses and what keyword to use for the
                    override.
        
        2. C{mandatory}: C{iterable} of keywords that subclasses must replace.
        
        3. C{replacements}: L{dict} that specifies the replacements to use in the
            subclass using the keywords defined in the C{repl_args} and 
            C{repl_kwargs} in a parent's C{Extend.fields} values.
            
        4. C{redelegate}: C{iterable} of field names from C{fields} in a
            parent's C{Extend} inner class that specifies which fields should not
            be added in this class but its subclass.

    Using the C{mandatory} field in a child class of C{Exendable} forces 
    grandchildren of to specify replacements for particular keywords.
    
    Grandchildren may further delegate adding fields to their own children i.e.
    the great grandchildren by specifying the field names in their C{redelegate}
    field of their inner C{Extend} class.

    For example: ::
    
        from django.db import models
        
        class OtherModel(models.Model): pass

        class OtherModelRel(models.Model):
            parent = models.ForeignKey("TestParent")
            other = models.ForeignKey(OtherModel)
        
        class YetAnotherModel(models.Model): pass
        
        class YetAnotherModelRel(models.Model):
            child = models.ForeignKey("TestChild")
            other = models.ForeignKey(YetAnotherModel)
        
        class TestParent(Extendable):
            class Extend:
                fields = {
                    'other': (models.ManyToManyField,
                              [OtherModel,],
                              {'through': OtherModelRel},
                              ['other_model',],
                              {'through': 'other_through'},
                             ),
                }
                mandatory = [
                    'other_through',
                ]

        class TestChild(TestParent):
            class Extend:
                replacements = {
                    'other_model': YetAnotherModel,
                    'other_through': YetAnotherModelRel,
                }
    '''
    
    objects = ExtendableManager()
    
    leaf_name = models.CharField(max_length=100, blank=True, editable=False)
    module_name = models.CharField(max_length=100, blank=True, editable=False)
    
    __metaclass__ = ExtendableMeta
    
    class Meta:
        abstract = True
        
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("leaf_name", self.__class__.__name__)
        kwargs.setdefault("module_name", self.__class__.__module__)
        super(Extendable, self).__init__(*args, **kwargs)
        
    def as_leaf_class(self):
        '''Return this instance as the farthest descendant of its class'''
        if self.is_instance_of(self.__class__):
            return self
        else:
            try:
                mod = import_module(self.module_name)
            except ImportError:
                logger.debug("init import error.")
                drop_to_shell(local=locals())
                raise
            klass = getattr(mod, self.leaf_name)
            return klass.objects.get(pk=self.pk)

    def is_instance_of(self, klass):
        """Is the object an instance of the passed class C{klass}?"""
        
        return self.leaf_name == klass.__name__ and self.module_name == klass.__module__
   
    '''
	Bypasses authentication limitations
    ''' 
    def straightSave(self):
	super(Extendable, self).save()	
    
