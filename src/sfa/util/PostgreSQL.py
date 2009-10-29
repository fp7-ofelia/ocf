#
# PostgreSQL database interface. Sort of like DBI(3) (Database
# independent interface for Perl).
#
#

import psycopg2
import psycopg2.extensions
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
# UNICODEARRAY not exported yet
psycopg2.extensions.register_type(psycopg2._psycopg.UNICODEARRAY)

import pgdb
from types import StringTypes, NoneType
import traceback
import commands
import re
from pprint import pformat

from sfa.util.faults import *
from sfa.util.debug import *

if not psycopg2:
    is8bit = re.compile("[\x80-\xff]").search

    def unicast(typecast):
        """
        pgdb returns raw UTF-8 strings. This function casts strings that
        apppear to contain non-ASCII characters to unicode objects.
        """
    
        def wrapper(*args, **kwds):
            value = typecast(*args, **kwds)

            # pgdb always encodes unicode objects as UTF-8 regardless of
            # the DB encoding (and gives you no option for overriding
            # the encoding), so always decode 8-bit objects as UTF-8.
            if isinstance(value, str) and is8bit(value):
                value = unicode(value, "utf-8")

            return value

        return wrapper

    pgdb.pgdbTypeCache.typecast = unicast(pgdb.pgdbTypeCache.typecast)

class PostgreSQL:
    def __init__(self, config):
        self.config = config
        self.debug = False
#        self.debug = True
        self.connection = None

    def cursor(self):
        if self.connection is None:
            # (Re)initialize database connection
            if psycopg2:
                try:
                    # Try UNIX socket first
                    self.connection = psycopg2.connect(user = self.config.SFA_PLC_DB_USER,
                                                       password = self.config.SFA_PLC_DB_PASSWORD,
                                                       database = self.config.SFA_PLC_DB_NAME)
                except psycopg2.OperationalError:
                    # Fall back on TCP
                    self.connection = psycopg2.connect(user = self.config.SFA_PLC_DB_USER,
                                                       password = self.config.SFA_PLC_DB_PASSWORD,
                                                       database = self.config.SFA_PLC_DB_NAME,
                                                       host = self.config.SFA_PLC_DB_HOST,
                                                       port = self.config.SFA_PLC_DB_PORT)
                self.connection.set_client_encoding("UNICODE")
            else:
                self.connection = pgdb.connect(user = self.config.SFA_PLC_DB_USER,
                                               password = self.config.SFA_PLC_DB_PASSWORD,
                                               host = "%s:%d" % (self.config.SFA_PLC_DB_HOST, self.config.SFA_PLC_DB_PORT),
                                               database = self.config.SFA_PLC_DB_NAME)

        (self.rowcount, self.description, self.lastrowid) = \
                        (None, None, None)

        return self.connection.cursor()

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

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

    quote = classmethod(quote)

    def param(self, name, value):
        # None is converted to the unquoted string NULL
        if isinstance(value, NoneType):
            conversion = "s"
        # True and False are also converted to unquoted strings
        elif isinstance(value, bool):
            conversion = "s"
        elif isinstance(value, float):
            conversion = "f"
        elif not isinstance(value, StringTypes):
            conversion = "d"
        else:
            conversion = "s"

        return '%(' + name + ')' + conversion

    param = classmethod(param)

    def begin_work(self):
        # Implicit in pgdb.connect()
        pass

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def do(self, query, params = None):
        cursor = self.execute(query, params)
        cursor.close()
        return self.rowcount

    def next_id(self, table_name, primary_key):
	sequence = "%(table_name)s_%(primary_key)s_seq" % locals()	
	sql = "SELECT nextval('%(sequence)s')" % locals()
	rows = self.selectall(sql, hashref = False)
	if rows: 
	    return rows[0][0]
		
	return None 

    def last_insert_id(self, table_name, primary_key):
        if isinstance(self.lastrowid, int):
            sql = "SELECT %s FROM %s WHERE oid = %d" % \
                  (primary_key, table_name, self.lastrowid)
            rows = self.selectall(sql, hashref = False)
            if rows:
                return rows[0][0]

        return None

    # modified for psycopg2-2.0.7 
    # executemany is undefined for SELECT's
    # see http://www.python.org/dev/peps/pep-0249/
    # accepts either None, a single dict, a tuple of single dict - in which case it execute's
    # or a tuple of several dicts, in which case it executemany's
    def execute(self, query, params = None):

        cursor = self.cursor()
        try:

            # psycopg2 requires %()s format for all parameters,
            # regardless of type.
            # this needs to be done carefully though as with pattern-based filters
            # we might have percents embedded in the query
            # so e.g. GetPersons({'email':'*fake*'}) was resulting in .. LIKE '%sake%'
            if psycopg2:
                query = re.sub(r'(%\([^)]*\)|%)[df]', r'\1s', query)
            # rewrite wildcards set by Filter.py as '***' into '%'
            query = query.replace ('***','%')

            if not params:
                if self.debug:
                    print >> log,'execute0',query
                cursor.execute(query)
            elif isinstance(params,dict):
                if self.debug:
                    print >> log,'execute-dict: params',params,'query',query%params
                cursor.execute(query,params)
            elif isinstance(params,tuple) and len(params)==1:
                if self.debug:
                    print >> log,'execute-tuple',query%params[0]
                cursor.execute(query,params[0])
            else:
                param_seq=(params,)
                if self.debug:
                    for params in param_seq:
                        print >> log,'executemany',query%params
                cursor.executemany(query, param_seq)
            (self.rowcount, self.description, self.lastrowid) = \
                            (cursor.rowcount, cursor.description, cursor.lastrowid)
        except Exception, e:
            try:
                self.rollback()
            except:
                pass
            uuid = commands.getoutput("uuidgen")
            print >> log, "Database error %s:" % uuid
            print >> log, e
            print >> log, "Query:"
            print >> log, query
            print >> log, "Params:"
            print >> log, pformat(params)
            raise GeniDBError("Please contact support")

        return cursor

    def selectall(self, query, params = None, hashref = True, key_field = None):
        """
        Return each row as a dictionary keyed on field name (like DBI
        selectrow_hashref()). If key_field is specified, return rows
        as a dictionary keyed on the specified field (like DBI
        selectall_hashref()).

        If params is specified, the specified parameters will be bound
        to the query.
        """

        cursor = self.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        self.commit()
        if hashref or key_field is not None:
            # Return each row as a dictionary keyed on field name
            # (like DBI selectrow_hashref()).
            labels = [column[0] for column in self.description]
            rows = [dict(zip(labels, row)) for row in rows]

        if key_field is not None and key_field in labels:
            # Return rows as a dictionary keyed on the specified field
            # (like DBI selectall_hashref()).
            return dict([(row[key_field], row) for row in rows])
        else:
            return rows

    def fields(self, table, notnull = None, hasdef = None):
        """
        Return the names of the fields of the specified table.
        """

        if hasattr(self, 'fields_cache'):
            if self.fields_cache.has_key((table, notnull, hasdef)):
                return self.fields_cache[(table, notnull, hasdef)]
        else:
            self.fields_cache = {}

        sql = "SELECT attname FROM pg_attribute, pg_class" \
              " WHERE pg_class.oid = attrelid" \
              " AND attnum > 0 AND relname = %(table)s"

        if notnull is not None:
            sql += " AND attnotnull is %(notnull)s"

        if hasdef is not None:
            sql += " AND atthasdef is %(hasdef)s"

        rows = self.selectall(sql, locals(), hashref = False)

        self.fields_cache[(table, notnull, hasdef)] = [row[0] for row in rows]

        return self.fields_cache[(table, notnull, hasdef)]
