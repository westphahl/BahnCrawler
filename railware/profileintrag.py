from datetime import datetime
import MySQLdb

from utils.db import Connection

INSERT_SQL = "INSERT INTO Profileintraege (bid_fk, zid_fk, geplanteAnkunft, erstelltAm, aktualisiertAm) VALUES (%s, %s, '%s', '%s', '%s')"
GET_SQL = "SELECT pid FROM Profileintraege WHERE bid_fk = %s AND zid_fk = %s"
UPDATE_SQL = "UPDATE Profileintraege SET aktualisiertAm = '%s' WHERE pid = %s"


class Profileintrag(object):

    def __init__(self, bahnhof, zug, ankunft):
        self.cursor = Connection.get_cursor()
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
            print("MySQL Error: %s" % str(e))

    def get_id(self):
        return self.id

    def __del__(self):
        self.cursor.close()
