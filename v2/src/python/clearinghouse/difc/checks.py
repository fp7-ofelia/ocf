'''
Created on Mar 9, 2010

@author: jnaous
'''
from clearinghouse.middleware import threadlocals

def _find_subsets(subsets, supersets):
    '''@summary: Find all sets in 'subsets' that are subsets of sets in 'supersets'
    
    @param subsets: Iterable of set instances in which to look for subsets
    @param supersets: Iterable of set instances in which to look for supersets
    
    @return: list of 2-tuples (subset, superset)
    '''
    
    return [(sub, sup) \
        for sub in subsets \
        for sup in supersets \
        if sub.issubset(sup)]

def _has_subsets(subsets, supersets):
    '''@summary: checks if there are sets in 'subsets' that are subsets of 
    sets in 'supersets'
    
    @param subsets: Iterable of set instances in which to look for subsets
    @param supersets: Iterable of set instances in which to look for supersets
    
    @return: True if found, false otherwise
    '''
    
    # special case for empty sets
    if not len(subsets): return True
    
    for sub in subsets:
        for sup in supersets:
            if sub.issubset(sup):
                return True

def can_flow(from_label, to_label):
#    '''@summary: Can information flow from from_label to 
#    to_label?
#    
#    This is true iff:
#        - There exists at least one set of categories in 'to_label''s
#          secrecy category sets that contains all the categories in at
#          least one set of categories in 'from_label''s cat. sets
#    And:
#        - There exists at least one set of categories in 'from_label''s
#          integrity category sets that contains all the categories in at
#          least one set of categories in 'to_label''s cat. sets
#    
#    @param from_label: 2-tuple (iterable of secrecy cats iterables, iterable of integrity cats iterables)
#    @param to_label: 2-tuple (iterable of secrecy cats iterables, iterable of integrity cats iterables)
#    
#    @return: True iff info can flow from from_label to to_label
#    '''
#
#    setitize = lambda(label): [set(cats) for cats in label]
#    from_s_set = setitize(from_label[0])
#    from_i_set = setitize(from_label[1])
#    to_s_set = setitize(to_label[0])
#    to_i_set = setitize(to_label[1])
#    
#    return _has_subsets(from_s_set, to_s_set) \
#        and _has_subsets(to_i_set, from_i_set)
    
    from_s_set = set(from_label[0])
    from_i_set = set(from_label[1])
    to_s_set = set(to_label[0])
    to_i_set = set(to_label[1])
    
    return from_s_set.issubset(to_s_set) and to_i_set.issubset(from_i_set)
    
def check_object_save(sender, **kwargs):
    '''Make sure that only the fields that are allowed to be written have
    been modified'''

    new_object = kwargs['instance']
    
    # get the old object from the db
    try:
        old_object = sender.objects.get(pk=new_object.pk)
    except sender.DoesNotExist:
        # The object is not in the database to begin with.
        return
    
    for field in old_object._meta.fields:
        # TODO: Check if changes to the labels are allowed.
        if not field.attname.endswith("_security_label") \
        and getattr(old_object, field.attname) != \
        getattr(new_object, field.attname):
            # check the current label and the field's label
            if not can_flow(
                threadlocals.get_current_label(),
                new_object.get_FIELD_label(field.attname)):
                raise SecurityException(
                    threadlocals.get_current_user(),
                    "Field %s cannot be modified." % field.attname)
            
class SecurityException(Exception):
    '''@summary: Exceptions caused by the difc app for this category
    
    @param user -- user who caused the exception
    @param msg -- explanation of the exception
    '''
    def __init__(self, user, msg):
        self.user = user
        self.msg = msg

            