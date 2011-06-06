import MySQLdb
import logging
from string import Template

from bahncrawler.utils.conf import settings
from bahncrawler.utils.db import connection

SELECT = Template("SELECT bid, name, uname FROM ${prefix}Bahnhoefe WHERE sid_fk = ${sid}").safe_substitute(prefix=settings['prefix'])


class Bahnhof(object):
    """Bahnhofsklasse fuer Zugriff auf DB-Tabelle."""

    def __init__(self, id, name, uname, strecke):
        """
        Initialisierungsmethode fuer einen Bahnhof.

        Bei Instanziierung eines Bahnhofs-Objektes wird kein Eintrag
        in der Datenbank erzeugt.
        """
        self.id = id
        self.name = name
        self.uname = uname
        self.strecke = strecke

    def get_name(self):
        """Get-Methode fuer Namen des Bahnhofs."""
        return self.name

    def get_uname(self):
        """Get-Methode fuer "Unique Name" des Bahnhofs."""
        return self.uname

    def get_id(self):
        """Get-Methode fuer ID (Primary Key) des Bahnhofs."""
        return self.id
    
    def get_strecke(self):
        """Get-Methode fuer die Strecke, welcher der Bahnhof zugeordnet ist."""
        return self.strecke

    @classmethod
    def get_all_for_strecke(cls, strecke):
        """
        Klassenmethod um alle Bahnhoefe einer bestimmten Strecke aus der
        Datenbank auszulesen.

        Die Methode bekommt ein Streckenobjekt uebergeben und liefert eine
        Liste mit Bahnhofs-Objekten zurueck.
        """
        cursor = connection.get_cursor()
        select_query = Template(SELECT).substitute(sid=long(strecke.get_id()))
        try:
            cursor.execute(select_query)
            if cursor.rowcount == 0:
                # keine Bahnhoefe vorhanden
                bahnhof_list = []
            else:
                result = cursor.fetchall()
                bahnhof_list = [Bahnhof(id, name, uname, strecke)
                        for id, name, uname in result]
            cursor.close()
            return bahnhof_list
        except MySQLdb.Error, e:
            logging.error("MySQL Error: %s" % str(e))
