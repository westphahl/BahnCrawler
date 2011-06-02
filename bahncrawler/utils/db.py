import MySQLdb
import logging

from bahncrawler.utils.conf import settings


class Connection(object):
    
    def __init__(self):
        try:
            self.con = MySQLdb.connect(
                    settings['host'],
                    settings['user'],
                    settings['password'],
                    settings['dbname'])
        except MySQLdb.OperationalError, e:
            logging.error("MySQL Error: %s", str(e))

    def get_cursor(self):
        try:
            return self.con.cursor()
        except MySQLdb.OperationalError, e:
            logging.error("MySQL Error: %s", str(e))

    def __del__(self):
        if hasattr(self.conf):
            self.con.close()


connection = Connection()
