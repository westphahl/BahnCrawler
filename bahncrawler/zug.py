import logging
import MySQLdb
from string import Template

from bahncrawler.utils.conf import settings
from bahncrawler.utils.db import connection

INSERT = Template("INSERT INTO ${prefix}Zuege (typ, nummer) VALUES " \
        "('${typ}', '${nummer}')").safe_substitute(prefix=settings['prefix'])

SELECT = Template("SELECT zid, typ, nummer FROM ${prefix}Zuege WHERE " \
        "typ = '${typ}' AND nummer = '${nummer}'"
        ).safe_substitute(prefix=settings['prefix'])


## Klasse Zug fuer den Datenbank-Zugriff.
class Zug(object):

    ## Initialisierungsmethode fuer einen Zug.
    #
    # Die Methode prueft, ob der Zug bereits in der Datenbank angelegt ist.
    # Ist dies nicht der Fall, so wird ein neuer Eintrag angelegt.
    # Das Objekt erhaelt einen eigenen Datenbank-Cursor
    #
    # \param[in] typ    Typ des Zuges (z.B. RE oder ICE)
    # \param[in] nr     Nr des Zuges
    def __init__(self, typ, nr):
        self._cursor = connection.get_cursor()
        select_query = Template(SELECT).substitute(typ=typ, nummer=nr)
        insert_query = Template(INSERT).substitute(typ=typ, nummer=nr)
        try:
            self._cursor.execute(select_query)
            if self._cursor.rowcount == 0:
                # kein Eintrag in der Datenbank
                self._cursor.execute(insert_query)
            self._cursor.execute(select_query)
            self._id, self._typ, self._nr = self._cursor.fetchone()
        except MySQLdb.Error, e:
            logging.error("MySQL Error: %s", str(e))

    ## Get-Methode fuer die ID (Primary Key) des Zuges.
    #
    # \return   Id des Zuges (Interger)
    def get_id(self):
        return self._id

    ## Schliessen des DB-Cursors, wenn das Objekt geloescht wird.
    def __del__(self):
        self._cursor.close()
