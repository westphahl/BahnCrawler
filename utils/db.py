import MySQLdb


host = '172.16.0.101'
port = 3306
user = 'crawler'
password = 'railware'
dbname = 'swenp01'


class Connection(object):
    
    con = None

    @classmethod
    def get_cursor(cls):
        try:
            if cls.con == None:
                cls.con = MySQLdb.connect(host, user, password, dbname)
            return cls.con.cursor()
        except MySQLdb.OperationalError, e:
            print("MySQL Error: %s" % str(e))

    @classmethod
    def close(cls):
        if cls.con != None:
            cls.con.close()