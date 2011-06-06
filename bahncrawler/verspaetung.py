import logging
from datetime import date
from string import Template
import MySQLdb

from bahncrawler.utils.conf import settings
from bahncrawler.utils.db import connection

SELECT = Template("SELECT vid FROM ${prefix}Verspaetungen WHERE pid_fk = ${pid} AND datum = '${datum}'").safe_substitute(prefix=settings['prefix'])
INSERT = Template("INSERT INTO ${prefix}Verspaetungen (pid_fk, minuten, datum) VALUES (${pid}, ${minuten}, '${datum}')").safe_substitute(prefix=settings['prefix'])
UPDATE = Template("UPDATE ${prefix}Verspaetungen SET minuten = ${minuten} WHERE pid_fk = ${pid} AND datum = '${datum}'").safe_substitute(prefix=settings['prefix'])


class Verspaetung(object):
    """Klasse Verspaetung fuer einen Profileintrag"""

    def __init__(self, profil, minuten):
        """
        Initialisierungsmethode fuer ein Verspaetungs-Objekt.

        Die Methode prueft, ob fuer den aktuellen Tag und Profileintrag
        bereits ein Verspaetungseintrag existiert. Falls vorhanden, wird die
        Verspaetung (in Minuten) aktualisiert oder andernfalls neu angelegt.
        Jedes Object erhaelt einen eigenen Datenbank Cursor.
        """
        self.cursor = connection.get_cursor()
        today = date.today()
        select_query = Template(SELECT).substitute(
                pid=profil.get_id(),
                datum=today.isoformat())
        insert_query = Template(INSERT).substitute(
                pid=profil.get_id(),
                minuten=minuten,
                datum=today.isoformat())
        update_query = Template(UPDATE).substitute(
                minuten=minuten,
                pid=profil.get_id(),
                datum=today.isoformat())
        try:
            self.cursor.execute(select_query)
            if self.cursor.rowcount == 0:
                # keine Verspaetung vorhanden
                self.cursor.execute(insert_query)
            else:
                self.cursor.execute(update_query)
        except MySQLdb.Error, e:
            logging.error("MySQL Error: %s" % str(e))

    def __del__(self):
        """Schliessen des DB Cursors, wenn das Objekt geloescht wird."""
        self.cursor.close()
