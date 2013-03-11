class String(object):

    def __init__(self, colname):
        self.name = colname

    @classmethod
    def validate(self, value):
        print "validating %r" % (value, )
        return value

class DBConnection(object):

    def query_cols(self, table):
        return [String('name'), String('amount')]
dbconn = DBConnection()

class DatabaseTable(type):

    def __init__(cls, name, bases, class_dict):
        #from dbsetup import dbconn
        col_defs = dbconn.query_cols(table=class_dict['dbtable'])
        for col_def in col_defs:

            dbcolumn = wrap_col_rdwr(col_def)
            setattr(cls, col_def.name, dbcolumn)

    def __new__(metatype, name, bases, class_dict):
        cls = type.__new__(metatype, name, bases, class_dict)
        return cls

def wrap_col_rdwr(col_def):

    def get_dbcol_value(self):
        return self.__dict__.get(col_def.name, None)

    def set_dbcol_value(self, value):
        value = col_def.validate(value)
        self.__dict__[col_def.name] = value

    return property(get_dbcol_value, set_dbcol_value)

class Member(object):
    __metaclass__ = DatabaseTable

    dbtable = 'Members'  # a declaration

m = Member()
print m.name, m.amount

m.amount = 123
