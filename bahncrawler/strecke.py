import MySQLdb
import logging
from string import Template

from bahncrawler.utils.conf import settings
from bahncrawler.utils.db import connection

SELECT = Template("SELECT sid from ${prefix}Strecken WHERE status = 1 ORDER BY erstelltAm DESC LIMIT 1").safe_substitute(prefix=settings['prefix'])


class Strecke(object):

    def __init__(self, id):
        self.cursor = connection.get_cursor()
        self.status_code = 1
        self.id = id

    def __del__(self):
        self.cursor.close()

    def __eq__(self, obj):
        if (isinstance(obj, self.__class__) and (self.id == obj.id)):
            return True
        else:
            return False

    def __ne__(self, obj):
        if (isinstance(obj, self.__class__) and (self.id == obj.id)):
            return False
        else:
            return True

    @classmethod
    def get_latest_strecke(cls):
        cursor = connection.get_cursor()
        try:
            cursor.execute(SELECT)
            if cursor.rowcount == 0:
                strecke = None
            else:
                strecke = Strecke(int(cursor.fetchone()[0]))
            cursor.close()
            return strecke
        except MySQLdb.Error, e:
            logging.error("MySQL Error: %s" % str(e))

    def get_id(self):
        return self.id

    def set_status(self, code, message):
        # TODO Status in Datenbank schreiben
        self.status_code = code
        self.status_message = message
