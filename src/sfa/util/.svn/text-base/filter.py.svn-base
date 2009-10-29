# $Id: Filter.py 14587 2009-07-19 13:18:50Z thierry $
# $URL: svn+ssh://svn.planet-lab.org/svn/PLCAPI/trunk/PLC/Filter.py $
from types import StringTypes
try:
    set
except NameError:
    from sets import Set
    set = Set

import time
import pgdb
 
from sfa.util.faults import *
from sfa.util.parameter import Parameter, Mixed, python_type


class Filter(Parameter, dict):
    """
    A type of parameter that represents a filter on one or more
    columns of a database table.
    Special features provide support for negation, upper and lower bounds, 
    as well as sorting and clipping.


    fields should be a dictionary of field names and types
    Only filters on non-sequence type fields are supported.
    example : fields = {'node_id': Parameter(int, "Node identifier"),
                        'hostname': Parameter(int, "Fully qualified hostname", max = 255),
                        ...}


    filter should be a dictionary of field names and values
    representing  the criteria for filtering. 
    example : filter = { 'hostname' : '*.edu' , site_id : [34,54] }
    Whether the filter represents an intersection (AND) or a union (OR) 
    of these criteria is determined by the join_with argument 
    provided to the sql method below

    Special features:

    * a field starting with the ~ character means negation.
    example :  filter = { '~peer_id' : None }

    * a field starting with < [  ] or > means lower than or greater than
      < > uses strict comparison
      [ ] is for using <= or >= instead
    example :  filter = { ']event_id' : 2305 }
    example :  filter = { '>time' : 1178531418 }
      in this example the integer value denotes a unix timestamp

    * if a value is a sequence type, then it should represent 
      a list of possible values for that field
    example : filter = { 'node_id' : [12,34,56] }

    * a (string) value containing either a * or a % character is
      treated as a (sql) pattern; * are replaced with % that is the
      SQL wildcard character.
    example :  filter = { 'hostname' : '*.jp' } 

    * fields starting with - are special and relate to row selection, i.e. sorting and clipping
    * '-SORT' : a field name, or an ordered list of field names that are used for sorting
      these fields may start with + (default) or - for denoting increasing or decreasing order
    example : filter = { '-SORT' : [ '+node_id', '-hostname' ] }
    * '-OFFSET' : the number of first rows to be ommitted
    * '-LIMIT' : the amount of rows to be returned 
    example : filter = { '-OFFSET' : 100, '-LIMIT':25}

    A realistic example would read
    GetNodes ( { 'node_type' : 'regular' , 'hostname' : '*.edu' , '-SORT' : 'hostname' , '-OFFSET' : 30 , '-LIMIT' : 25 } )
    and that would return regular (usual) nodes matching '*.edu' in alphabetical order from 31th to 55th
    """

    def __init__(self, fields = {}, filter = {}, doc = "Attribute filter"):
        # Store the filter in our dict instance
        valid_fields = {}
        for field in filter:
            if field in fields:
                valid_fields[field] = filter[field]
        dict.__init__(self, valid_fields)

        # Declare ourselves as a type of parameter that can take
        # either a value or a list of values for each of the specified
        # fields.
        self.fields = dict ( [ ( field, Mixed (expected, [expected])) 
                                 for (field,expected) in fields.iteritems()
                                 if python_type(expected) not in (list, tuple, set) ] )

        # Null filter means no filter
        Parameter.__init__(self, self.fields, doc = doc, nullok = True)

    def quote(self, value):
        """
        Returns quoted version of the specified value.
        """

        # The pgdb._quote function is good enough for general SQL
        # quoting, except for array types.
        if isinstance(value, (list, tuple, set)):
            return "ARRAY[%s]" % ", ".join(map, self.quote, value)
        else:
            return pgdb._quote(value)    

    def sql(self, join_with = "AND"):
        """
        Returns a SQL conditional that represents this filter.
        """

        # So that we always return something
        if join_with == "AND":
            conditionals = ["True"]
        elif join_with == "OR":
            conditionals = ["False"]
        else:
            assert join_with in ("AND", "OR")

        # init 
        sorts = []
        clips = []

        for field, value in self.iteritems():
	    # handle negation, numeric comparisons
	    # simple, 1-depth only mechanism

	    modifiers={'~' : False, 
		       '<' : False, '>' : False,
		       '[' : False, ']' : False,
                       '-' : False,
		       }

	    for char in modifiers.keys():
		if field[0] == char:
		    modifiers[char]=True;
		    field = field[1:]
		    break

            # filter on fields
            if not modifiers['-']:
                if field not in self.fields:
                    raise GeniInvalidArgument, "Invalid filter field '%s'" % field

                if isinstance(value, (list, tuple, set)):
                    # handling filters like '~slice_id':[]
                    # this should return true, as it's the opposite of 'slice_id':[] which is false
                    # prior to this fix, 'slice_id':[] would have returned ``slice_id IN (NULL) '' which is unknown 
                    # so it worked by coincidence, but the negation '~slice_ids':[] would return false too
                    if not value:
                        field=""
                        operator=""
                        value = "FALSE"
                    else:
                        operator = "IN"
                        value = map(str, map(self.quote, value))
                        value = "(%s)" % ", ".join(value)
                else:
                    if value is None:
                        operator = "IS"
                        value = "NULL"
                    elif isinstance(value, StringTypes) and \
                            (value.find("*") > -1 or value.find("%") > -1):
                        operator = "LIKE"
                        # insert *** in pattern instead of either * or %
                        # we dont use % as requests are likely to %-expansion later on
                        # actual replacement to % done in PostgreSQL.py
                        value = value.replace ('*','***')
                        value = value.replace ('%','***')
                        value = str(self.quote(value))
                    else:
                        operator = "="
                        if modifiers['<']:
                            operator='<'
                        if modifiers['>']:
                            operator='>'
                        if modifiers['[']:
                            operator='<='
                        if modifiers[']']:
                            operator='>='
                        else:
                            value = str(self.quote(value))
 
                clause = "%s %s %s" % (field, operator, value)

                if modifiers['~']:
                    clause = " ( NOT %s ) " % (clause)

                conditionals.append(clause)
            # sorting and clipping
            else:
                if field not in ('SORT','OFFSET','LIMIT'):
                    raise GeniInvalidArgument, "Invalid filter, unknown sort and clip field %r"%field
                # sorting
                if field == 'SORT':
                    if not isinstance(value,(list,tuple,set)):
                        value=[value]
                    for field in value:
                        order = 'ASC'
                        if field[0] == '+':
                            field = field[1:]
                        elif field[0] == '-':
                            field = field[1:]
                            order = 'DESC'
                        if field not in self.fields:
                            raise GeniInvalidArgument, "Invalid field %r in SORT filter"%field
                        sorts.append("%s %s"%(field,order))
                # clipping
                elif field == 'OFFSET':
                    clips.append("OFFSET %d"%value)
                # clipping continued
                elif field == 'LIMIT' :
                    clips.append("LIMIT %d"%value)

        where_part = (" %s " % join_with).join(conditionals)
        clip_part = ""
        if sorts:
            clip_part += " ORDER BY " + ",".join(sorts)
        if clips:
            clip_part += " " + " ".join(clips)
#	print 'where_part=',where_part,'clip_part',clip_part
        return (where_part,clip_part)
