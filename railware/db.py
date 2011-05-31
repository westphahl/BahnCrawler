import pymysql

class DBConnection(object):

    _connection = None

    def __init__(self, host, user, password, dbname):
        if (DBConnection._connection == None):
            DBConnection._connection = pymysql.connect(
                    host, user, password, dbname)

