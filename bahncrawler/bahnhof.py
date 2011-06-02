import MySQLdb
import logging

from bahncrawler.utils.conf import settings
from bahncrawler.utils.db import connection

GET_SQL = "SELECT bid, name, uname FROM " + settings['prefix'] + "Bahnhoefe WHERE sid_fk = %s"


class Bahnhof(object):

    def __init__(self, id, name, uname, strecke):
        self.id = id
        self.name = name
        self.uname = uname
        self.strecke = strecke
        self.cursor = connection.get_cursor()

    def __del__(self):
        self.cursor.close()

    def get_name(self):
        return self.name

    def get_uname(self):
        return self.uname

    def get_id(self):
        return self.id
    
    def get_strecke(self):
        return self.strecke

    @classmethod
    def get_all_for_strecke(cls, strecke):
        cursor = connection.get_cursor()
        try:
            cursor.execute(GET_SQL % long(strecke.id))
            if cursor.rowcount == 0:
                bahnhof_list = []
            else:
                result = cursor.fetchall()
                bahnhof_list = [Bahnhof(id, name, uname, strecke)
                        for id, name, uname in result]
            cursor.close()
            return bahnhof_list
        except MySQLdb.Error, e:
            logging.error("MySQL Error: %s" % str(e))
