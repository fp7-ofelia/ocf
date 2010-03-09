'''
Created on Feb 23, 2010

@author: jnaous
'''
from django.db.models.query import QuerySet, Q
from django.db.models import sql

class SecureQuery(sql.Query):
    '''Implements a secure query that does not return hidden/secret data'''
    
    def results_iter(self):
        '''Add filters to remove hidden/secret data from results'''
    
        from clearinghouse.middleware import threadlocals
        
        # get the user requesting the query set
        user = threadlocals.get_current_user()

        # NOTE: by default objects that are not related to the user through
        #       a SecurityRole instance won't be considered, so won't be seen.
        if 'protect_roleless_objects' not in self.__dict__:
            self.protect_roleless_objects = True
            
        if self.protect_roleless_objects:
            # filter out any objects that are not related to the current user
            self.add_q(
                Q(**{self.model.get_security_related_users_name():user}))
            self.add_select_related(
                [self.model.get_security_related_roles_name()]) 

#        print "+++++++++++++++++++++++++++++++++++++"
#        print "Executing secure_results_iter"
#        print "\nas_sql:"
#        print self.as_sql()
#        print "\nwhere:"
#        print self.where
#        print "\nextra_where:"
#        print self.extra_where
#        print "\nselect:"
#        print self.select
#        print "\nget_columns:"
#        print self.get_columns()
#        print "+++++++++++++++++++++++++++++++++++++"
        return super(SecureQuery, self).results_iter()
    
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
        
        # TODO: need to filter out objects where the query was
        # based on a hidden field
