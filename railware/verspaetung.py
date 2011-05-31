from datetime import date
import MySQLdb

from utils.db import Connection

INSERT_SQL = "INSERT INTO Verspaetungen (pid_fk, minuten, datum) VALUES (%s, %s, '%s')"
GET_SQL = "SELECT vid FROM Verspaetungen WHERE pid_fk = %s AND datum = '%s'"
UPDATE_SQL = "UPDATE Verspaetungen SET minuten = %s WHERE pid_fk = %s AND datum = '%s'"


class Verspaetung(object):

    def __init__(self, profil, minuten):
        self.cursor = Connection.get_cursor()
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
            print("MySQL Error: %s" % str(e))

    def __del__(self):
        self.cursor.close()
