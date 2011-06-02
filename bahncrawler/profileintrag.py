import logging
from datetime import datetime
import MySQLdb

from bahncrawler.utils.conf import settings
from bahncrawler.utils.db import connection

INSERT_SQL = "INSERT INTO " + settings['prefix'] + "Profileintraege (bid_fk, zid_fk, geplanteAnkunft, erstelltAm, aktualisiertAm) VALUES (%s, %s, '%s', '%s', '%s')"
GET_SQL = "SELECT pid FROM " + settings['prefix'] + "Profileintraege WHERE bid_fk = %s AND zid_fk = %s"
UPDATE_SQL = "UPDATE " + settings['prefix'] + "Profileintraege SET aktualisiertAm = '%s' WHERE pid = %s"


class Profileintrag(object):

    def __init__(self, bahnhof, zug, ankunft):
        self.cursor = connection.get_cursor()
        try:
            now = datetime.now()
            self.cursor.execute(GET_SQL % (bahnhof.get_id(), zug.get_id()))
            if self.cursor.rowcount == 0:
                self.cursor.execute(INSERT_SQL % (
                    bahnhof.get_id(),
                    zug.get_id(),
                    ankunft.strftime('%H:%M:%S'),
                    now.strftime('%Y-%m-%d %H:%M:%S'),
                    now.strftime('%Y-%m-%d %H:%M:%S')))
            else:
                result = self.cursor.fetchone()
                self.cursor.execute(UPDATE_SQL % (
                    now.strftime('%Y-%m-%d %H:%M:%S'),
                    result[0]))
            self.cursor.execute(GET_SQL % (bahnhof.get_id(), zug.get_id()))
            self.id = self.cursor.fetchone()[0]
        except MySQLdb.Error, e:
            logging.error("MySQL Error: %s", str(e))

    def get_id(self):
        return self.id

    def __del__(self):
        self.cursor.close()
