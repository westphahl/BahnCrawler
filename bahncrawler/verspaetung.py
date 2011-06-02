import logging
from datetime import date
import MySQLdb

from bahncrawler.utils.conf import settings
from bahncrawler.utils.db import connection

INSERT_SQL = "INSERT INTO " + settings['prefix'] + "Verspaetungen (pid_fk, minuten, datum) VALUES (%s, %s, '%s')"
GET_SQL = "SELECT vid FROM " + settings['prefix'] + "Verspaetungen WHERE pid_fk = %s AND datum = '%s'"
UPDATE_SQL = "UPDATE " + settings['prefix'] + "Verspaetungen SET minuten = %s WHERE pid_fk = %s AND datum = '%s'"


class Verspaetung(object):

    def __init__(self, profil, minuten):
        self.cursor = connection.get_cursor()
        try:
            today = date.today()
            self.cursor.execute(GET_SQL % (profil.get_id(), today.isoformat()))
            if self.cursor.rowcount == 0:
                self.cursor.execute(INSERT_SQL % (
                    profil.get_id(),
                    minuten,
                    today.isoformat()))
            else:
                self.cursor.execute(UPDATE_SQL % (
                    minuten,
                    profil.get_id(),
                    today.isoformat()))
            self.cursor.execute(GET_SQL % (profil.get_id(), today.isoformat()))
        except MySQLdb.Error, e:
            logging.error("MySQL Error: %s" % str(e))

    def __del__(self):
        self.cursor.close()
