import MySQLdb

from bahncrawler.utils.conf import settings


class Connection(object):
    
    def __init__(self):
        try:
            self.con = MySQLdb.connect(
                    settings['dbhost'],
                    settings['dbuser'],
                    settings['dbpassword'],
                    settings['dbname'])
        except MySQLdb.OperationalError, e:
            print("MySQL Error: %s" % str(e))

    def get_cursor(self):
        try:
            return self.con.cursor()
        except MySQLdb.OperationalError, e:
            print("MySQL Error: %s" % str(e))

    def __del__(self):
        self.con.close()


connection = Connection()
