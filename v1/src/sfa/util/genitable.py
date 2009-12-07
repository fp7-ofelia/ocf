# genitable.py
#
# implements support for geni records stored in db tables
#
# TODO: Use existing PLC database methods? or keep this separate?

### $Id: genitable.py 15170 2009-09-27 00:49:17Z tmack $
### $URL: http://svn.planet-lab.org/svn/sfa/tags/sfa-0.9-5/sfa/util/genitable.py $

import report
import  pgdb
from pg import DB, ProgrammingError
from sfa.util.PostgreSQL import *
from sfa.trust.gid import *
from sfa.util.record import *
from sfa.util.debug import *
from sfa.util.config import *
from sfa.util.filter import *

class GeniTable(list):

    GENI_TABLE_PREFIX = "sfa"

    def __init__(self, record_filter = None):

        # pgsql doesn't like table names with "." in them, to replace it with "$"
        self.tablename = GeniTable.GENI_TABLE_PREFIX
        self.config = Config()
        self.db = PostgreSQL(self.config)
        # establish a connection to the pgsql server
        cninfo = self.config.get_plc_dbinfo()     
        self.cnx = DB(cninfo['dbname'], cninfo['address'], port=cninfo['port'], user=cninfo['user'], passwd=cninfo['password'])

        if record_filter:
            records = self.find(record_filter)
            for record in reocrds:
                self.append(record)             

    def exists(self):
        tableList = self.cnx.get_tables()
        if 'public.' + self.tablename in tableList:
            return True
        if 'public."' + self.tablename + '"' in tableList:
            return True
        return False

    def db_fields(self, obj=None):
        
        db_fields = self.db.fields(self.GENI_TABLE_PREFIX)
        return dict( [ (key,value) for (key, value) in obj.items() \
                        if key in db_fields and
                        self.is_writable(key, value, GeniRecord.fields)] )      

    @staticmethod
    def is_writable (key,value,dict):
        # if not mentioned, assume it's writable (e.g. deleted ...)
        if key not in dict: return True
        # if mentioned but not linked to a Parameter object, idem
        if not isinstance(dict[key], Parameter): return True
        # if not marked ro, it's writable
        if not dict[key].ro: return True

        return False

    def create(self):
        
        querystr = "CREATE TABLE " + self.tablename + " ( \
                record_id serial PRIMARY KEY , \
                hrn text NOT NULL, \
                authority text NOT NULL, \
                peer_authority text, \
                gid text, \
                type text NOT NULL, \
                pointer integer, \
                date_created timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP, \
                last_updated timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP);"
        template = "CREATE INDEX %s_%s_idx ON %s (%s);"
        indexes = [template % ( self.tablename, field, self.tablename, field) \
                   for field in ['hrn', 'type', 'authority', 'peer_authority', 'pointer']]
        # IF EXISTS doenst exist in postgres < 8.2
        try:
            self.cnx.query('DROP TABLE IF EXISTS ' + self.tablename)
        except ProgrammingError:
            try:
                self.cnx.query('DROP TABLE ' + self.tablename)
            except ProgrammingError:
                pass
         
        self.cnx.query(querystr)
        for index in indexes:
            self.cnx.query(index)

    def remove(self, record):
        query_str = "DELETE FROM %s WHERE record_id = %s" % (self.tablename, record['record_id']) 
        self.cnx.query(query_str)

    def insert(self, record):
        db_fields = self.db_fields(record)
        keys = db_fields.keys()
        values = [self.db.param(key, value) for (key, value) in db_fields.items()]
        query_str = "INSERT INTO " + self.tablename + \
                       "(" + ",".join(keys) + ") " + \
                       "VALUES(" + ",".join(values) + ")"
        self.db.do(query_str, db_fields)
        self.db.commit()
        result = self.find({'hrn': record['hrn'], 'type': record['type'], 'peer_authority': record['peer_authority']})
        if not result:
            record_id = None
        elif isinstance(result, list):
            record_id = result[0]['record_id']
        else:
            record_id = result['record_id']

        return record_id

    def update(self, record):
        db_fields = self.db_fields(record)
        keys = db_fields.keys()
        values = [self.db.param(key, value) for (key, value) in db_fields.items()]
        columns = ["%s = %s" % (key, value) for (key, value) in zip(keys, values)]
        query_str = "UPDATE %s SET %s WHERE record_id = %s" % \
                    (self.tablename, ", ".join(columns), record['record_id'])
        self.db.do(query_str, db_fields)
        self.db.commit()

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

    def find(self, record_filter = None):
        sql = "SELECT * FROM %s WHERE True " % self.tablename
        
        if isinstance(record_filter, (list, tuple, set)):
            ints = filter(lambda x: isinstance(x, (int, long)), record_filter)
            strs = filter(lambda x: isinstance(x, StringTypes), record_filter)
            record_filter = Filter(GeniRecord.all_fields, {'record_id': ints, 'hrn': strs})
            sql += "AND (%s) %s " % record_filter.sql("OR") 
        elif isinstance(record_filter, dict):
            record_filter = Filter(GeniRecord.all_fields, record_filter)        
            sql += " AND (%s) %s" % record_filter.sql("AND")
        elif isinstance(record_filter, StringTypes):
            record_filter = Filter(GeniRecord.all_fields, {'hrn':[record_filter]})    
            sql += " AND (%s) %s" % record_filter.sql("AND")
        elif isinstance(record_filter, int):
            record_filter = Filter(GeniRecord.all_fields, {'record_id':[record_filter]})    
            sql += " AND (%s) %s" % record_filter.sql("AND")

        results = self.cnx.query(sql).dictresult()
        if isinstance(results, dict):
            results = [results]
        return results

    def findObjects(self, record_filter = None):
        
        results = self.find(record_filter) 
        result_rec_list = []
        for result in results:
            if result['type'] in ['authority']:
                result_rec_list.append(AuthorityRecord(dict=result))
            elif result['type'] in ['node']:
                result_rec_list.append(NodeRecord(dict=result))
            elif result['type'] in ['slice']:
                result_rec_list.append(SliceRecord(dict=result))
            elif result['type'] in ['user']:
                result_rec_list.append(UserRecord(dict=result))
            else:
                result_rec_list.append(GeniRecord(dict=result))
        return result_rec_list


    def drop(self):
        try:
            self.cnx.query('DROP TABLE IF EXISTS ' + self.tablename)
        except ProgrammingError:
            try:
                self.cnx.query('DROP TABLE ' + self.tablename)
            except ProgrammingError:
                pass
    
    @staticmethod
    def geni_records_purge(cninfo):

        cnx = DB(cninfo['dbname'], cninfo['address'], 
                 port=cninfo['port'], user=cninfo['user'], passwd=cninfo['password'])
        tableList = cnx.get_tables()
        for table in tableList:
            if table.startswith(GeniTable.GENI_TABLE_PREFIX) or \
                    table.startswith('public.' + GeniTable.GENI_TABLE_PREFIX) or \
                    table.startswith('public."' + GeniTable.GENI_TABLE_PREFIX):
                report.trace("dropping table " + table)
                cnx.query("DROP TABLE " + table)
