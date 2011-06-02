import MySQLdb
import logging

from bahncrawler.utils.conf import settings
from bahncrawler.utils.db import connection

INSERT_SQL = "INSERT INTO " + settings['prefix'] + "Zuege (typ, nummer) VALUES ('%s', '%s')"
GET_SQL = "SELECT zid, typ, nummer FROM " + settings['prefix'] + "Zuege WHERE typ = '%s' AND nummer = '%s'"


class Zug(object):

    def __init__(self, typ, nr):
        self.cursor = connection.get_cursor()
        try:
            self.cursor.execute(GET_SQL % (typ, nr))
            if self.cursor.rowcount == 0:
                self.cursor.execute(INSERT_SQL % (typ, nr))
            self.cursor.execute(GET_SQL % (typ, nr))
            self.id, self.typ, self.nr = self.cursor.fetchone()
        except MySQLdb.Error, e:
            logging.error("MySQL Error: %s", str(e))

    def get_id(self):
        return self.id

    def __del__(self):
        self.cursor.close()
