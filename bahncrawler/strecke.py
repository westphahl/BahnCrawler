import MySQLdb
import logging
from string import Template

from bahncrawler.utils.conf import settings
from bahncrawler.utils.db import connection

SELECT = Template("SELECT sid from ${prefix}Strecken WHERE status = 1 ORDER BY erstelltAm DESC LIMIT 1").safe_substitute(prefix=settings['prefix'])


class Strecke(object):
    """Streckenklasse fuer Zugriff auf Datenbanktabelle."""

    def __init__(self, id):
        self.status_code = 1
        self.id = id

    def __eq__(self, obj):
        """Methode fuer "==" (equal) Vergleiche."""
        if (isinstance(obj, self.__class__) and (self.id == obj.id)):
            return True
        else:
            return False

    def __ne__(self, obj):
        """Methode fuer "!=" (not equal) Vergleiche."""
        if (isinstance(obj, self.__class__) and (self.id == obj.id)):
            return False
        else:
            return True

    @classmethod
    def get_latest_strecke(cls):
        """
        Klassenmethode um die neuste Strecke aus der Datenbank abzufragen.

        Die Methode gibt ein Strecken-Objekt zurueck.
        """
        cursor = connection.get_cursor()
        try:
            cursor.execute(SELECT)
            if cursor.rowcount == 0:
                # keine gueltige Strecke in der Datenbank
                strecke = None
            else:
                strecke = Strecke(int(cursor.fetchone()[0]))
            cursor.close()
            return strecke
        except MySQLdb.Error, e:
            logging.error("MySQL Error: %s" % str(e))

    def get_id(self):
        """Get-Methode fuer ID (Primary Key) der Strecke."""
        return self.id

    def set_status(self, code, message):
        """
        Set-Method um Status der Strecke zu setzen.

        Gueltige Status-Codes:
            0 = nicht bearbeitet (d.h. noch keine Bahnhoefe angelegt)
            1 = ok
            2 = fehlerhaft
        """
        # TODO Status in Datenbank schreiben
        self.status_code = code
        self.status_message = message
