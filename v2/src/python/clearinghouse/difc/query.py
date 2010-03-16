'''
Created on Feb 23, 2010

@author: jnaous
'''
from django.db.models.query import QuerySet, Q
from django.db.models import sql
from django.conf import settings
from django.utils.tree import Node
from django.db.models.sql.constants import LOOKUP_SEP, QUERY_TERMS
from clearinghouse.difc.models import SecureModel, SecureModelBase, Category
from clearinghouse.middleware import threadlocals

class SecureQuery(sql.Query):
    '''Implements a secure query that does not return hidden/secret data'''
    
    def add_q(self, q_object, used_aliases=None):
        super(SecureQuery, self).add_q(q_object, used_aliases)
        
        curr_s_lbl, curr_i_lbl = threadlocals.get_current_label()
        
        # get all tree tuples
        def get_tuples(node):
            if not isinstance(node, Node):
                return [node[0]]
            l = []
            for c in node.children:
                l.extend(get_tuples(c))
            return l

        child_tuples = get_tuples(q_object)
        
        # for each applied filter
        for t in child_tuples:
            parts = t.split(LOOKUP_SEP)
            opts = self.get_meta()
            # Now for each part, check if the owning model is a SecureModel
            # then add label filters
            owner_class = self.model
            for pos, name in enumerate(parts):
                if name.endswith("_secrecy_label")\
                or name.endswith("_integrity_label"):
                    # Don't add label filters for label!
                    continue
                
                if name in QUERY_TERMS:
                    continue
                
                if name == 'pk' or name == 'id':
                    continue
                    
                # Get the info about the field
                field, model, direct, m2m = opts.get_field_by_name(name)
                if isinstance(owner_class, SecureModelBase):
                    # get the label filter predicates
                    new_s_f = "%s%s" % (
                        "__".join(parts[:pos] + "__" if pos else ""), # all prev flds
                        owner_class.__metaclass__.get_secrecy_label_name(name))
                    new_i_f = "%s%s" % (
                        "__".join(parts[:pos] + "__" if pos else ""), # all prev flds
                        owner_class.__metaclass__.get_integrity_label_name(name))
                    # add filters for all categories
                    if not curr_s_lbl:
                        super(SecureQuery, self).add_q(
                            Q(**{new_s_f: None}))
                    else:
                        # get the list of all category ids
                        curr_s_lbl_ids = [c.pk for c in curr_s_lbl]
                        other_cats = list(Category.objects.filter(~Q(
                            id__in=curr_s_lbl_ids)))
                        super(SecureQuery, self).add_q(
                            ~Q(**{"%s__in" % new_s_f: other_cats}))
                    for c in curr_i_lbl:
                        self.add_q(Q(**{new_i_f: c}))
                    
                if direct:
                    if field.rel:
                        # a related field, so check if SecureModel
                        owner_class = field.rel.to
                        opts = field.rel.to._meta
                else:
                    # TODO: What do we do about indirect rels?
                    pass
        
#    def results_iter(self):
#        '''Add filters to remove hidden/secret data from results'''
#    
##        from clearinghouse.middleware import threadlocals
##        
##        curr_label = threadlocals.get_current_label()
#        
##        # get the user requesting the query set
##        user = threadlocals.get_current_user()
##
##        # NOTE: by default objects that are not related to the user through
##        #       a SecurityRole instance won't be considered, so won't be seen.
##        if 'protect_roleless_objects' not in self.__dict__:
##            self.protect_roleless_objects = True
##            
##        if self.protect_roleless_objects:
##            # filter out any objects that are not related to the current user
##            self.add_q(
##                Q(**{self.model.get_security_related_users_name():user}))
##            self.add_select_related(
##                [self.model.get_security_related_roles_name()]) 
##
##        print "+++++++++++++++++++++++++++++++++++++"
##        print "Executing secure_results_iter"
##        print "\nas_sql:"
##        print self.as_sql()
##        print "\nwhere:"
##        print self.where
##        
#        # get all where predicate tuples
#        def get_tuples(node):
#            if isinstance(node, tuple):
#                return [node[0]]
#            l = []
#            for c in node.children:
#                l.extend(get_tuples(c))
#            return l
#        
#        wheres = get_tuples(self.where)
#        
#        curr_s_lbl, curr_i_lbl = threadlocals.get_current_label()
#        
#        # for each where tuple, check if the model is a SecureModel
##        for w in wheres:
##            if w[0] in settings.secure_models:
##                s_lbl, i_lbl = self.get_FIELD_label(w[1])
##                for c in curr_s_lbl:
##                    self.add_q(Q(**{}))
#        # TODO: For each field, add the label. Need to go through __
#        
##        print "\nextra_where:"
##        print self.extra_where
##        print "\nselect:"
##        print self.select
##        print "\nget_columns:"
##        print self.get_columns()
##        print "+++++++++++++++++++++++++++++++++++++"
#        return super(SecureQuery, self).results_iter()

    def clone(self, *args, **kwargs):
        c = super(SecureQuery, self).clone(*args, **kwargs)
        return c
    
    
class SecureQuerySet(QuerySet):
    '''Implements most of the normal Django QuerySet methods
    but always returns items that the user is allowed to see.'''
    
    def __init__(self, *args, **kwargs):
        super(SecureQuerySet, self).__init__(*args, **kwargs)
        self.query = self.query.clone(
            klass=SecureQuery)
