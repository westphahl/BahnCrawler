import MySQLdb
import logging
from string import Template

from bahncrawler.utils.conf import settings
from bahncrawler.utils.db import connection

INSERT = Template("INSERT INTO ${prefix}Zuege (typ, nummer) VALUES ('${typ}', '${nummer}')").safe_substitute(prefix=settings['prefix'])
SELECT = Template("SELECT zid, typ, nummer FROM ${prefix}Zuege WHERE typ = '${typ}' AND nummer = '${nummer}'").safe_substitute(prefix=settings['prefix'])


class Zug(object):
    """Klasse Zug fuer den Datenbank-Zugriff."""

    def __init__(self, typ, nr):
        """
        Initialisierungsmethode fuer einen Zug.

        Die Methode pruef, ob der Zug bereits in der Datenbank angelegt ist.
        Ist dies nicht der Fall, so wird ein neuer Eintrag angelegt.
        Das Objekt erhaelt einen eigenen Datenbank-Cursor
        """
        self.cursor = connection.get_cursor()
        select_query = Template(SELECT).substitute(typ=typ, nummer=nr)
        insert_query = Template(INSERT).substitute(typ=typ, nummer=nr)
        try:
            self.cursor.execute(select_query)
            if self.cursor.rowcount == 0:
                # kein Eintrag in der Datenbank
                self.cursor.execute(insert_query)
            self.cursor.execute(select_query)
            self.id, self.typ, self.nr = self.cursor.fetchone()
        except MySQLdb.Error, e:
            logging.error("MySQL Error: %s", str(e))

    def get_id(self):
        """Get-Methode fuer die ID (Primary Key) des Zuges."""
        return self.id

    def __del__(self):
        """Schliessen des DB-Cursors, wenn das Objekt geloescht wird."""
        self.cursor.close()
