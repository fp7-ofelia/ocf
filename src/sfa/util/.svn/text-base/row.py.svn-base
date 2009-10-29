
class Row(dict):

    # Set this to the name of the table that stores the row.
    # e.g. table_name = "nodes"
    table_name = None

    # Set this to the name of the primary key of the table. It is
    # assumed that the this key is a sequence if it is not set when
    # sync() is called.
    # e.g. primary_key="record_id"
    primary_key = None

    # Set this to the names of tables that reference this table's
    # primary key.
    join_tables = []

    def validate(self):
        """
        Validates values. Will validate a value with a custom function
        if a function named 'validate_[key]' exists.
        """
        # Warn about mandatory fields
        # XX TODO: Support checking for mandatory fields later
        #mandatory_fields = self.db.fields(self.table_name, notnull = True, hasdef = False)
        #for field in mandatory_fields:
        #    if not self.has_key(field) or self[field] is None:
        #        raise GeniInvalidArgument, field + " must be specified and cannot be unset in class %s"%self.__class__.__name__

        # Validate values before committing
        for key, value in self.iteritems():
            if value is not None and hasattr(self, 'validate_' + key):
                validate = getattr(self, 'validate_' + key)
                self[key] = validate(value)


    def validate_timestamp(self, timestamp, check_future = False):
        """
        Validates the specified GMT timestamp string (must be in
        %Y-%m-%d %H:%M:%S format) or number (seconds since UNIX epoch,
        i.e., 1970-01-01 00:00:00 GMT). If check_future is True,
        raises an exception if timestamp is not in the future. Returns
        a GMT timestamp string.
        """

        time_format = "%Y-%m-%d %H:%M:%S"
        if isinstance(timestamp, StringTypes):
            # calendar.timegm() is the inverse of time.gmtime()
            timestamp = calendar.timegm(time.strptime(timestamp, time_format))

        # Human readable timestamp string
        human = time.strftime(time_format, time.gmtime(timestamp))

        if check_future and timestamp < time.time():
            raise GeniInvalidArgument, "'%s' not in the future" % human

        return human
