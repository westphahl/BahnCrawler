import logging
import MySQLdb
from datetime import datetime
from string import Template

from bahncrawler.utils.conf import settings
from bahncrawler.utils.db import connection

INSERT = Template("INSERT INTO ${prefix}Profileintraege (bid_fk, zid_fk, " \
        "geplanteAnkunft, erstelltAm, aktualisiertAm, erfassungsZaehler) " \
        "VALUES (${bid}, ${zid}, '${ankunft}', '${erstellt}', " \
        "'${aktualisiert}', ${counter})"
        ).safe_substitute(prefix=settings['prefix'])

SELECT = Template("SELECT pid, aktualisiertAm, erfassungsZaehler FROM " \
        "${prefix}Profileintraege WHERE bid_fk = ${bid} AND zid_fk = ${zid}"
        ).safe_substitute(prefix=settings['prefix'])

UPDATE = Template("UPDATE ${prefix}Profileintraege SET aktualisiertAm = " \
        "'${aktualisiert}', erfassungsZaehler = ${counter} WHERE pid = ${pid}"
        ).safe_substitute(prefix=settings['prefix'])


## Klasse Profileintrag fuer einen Zug an einem Bahnhof
class Profileintrag(object):

    ## Initialisierungsmethode fuer einen Profileintrag.
    #
    # Wird ein Profileintrag instanziiert, so wird zuerst versucht diesen aus
    # der Datenbank abzufragen. Existiert noch kein passender Eintrag, so
    # wird dieser erzeugt.
    # Jede Instanz eines erhaelt einen eigenen Datebank Cursor.
    #
    # \param[in] bahnhof    Bahnhofs-Objekt fuer die Zuordnung
    # \param[in] zug        Zug-Object fuer die Zuordnung
    # \param[in] ankunft    Ankunfszeit fuer einen Zug am Bahnhof
    def __init__(self, bahnhof, zug, ankunft):
        self.cursor = connection.get_cursor()
        now = datetime.now()
        select_query = Template(SELECT).substitute(
                bid=bahnhof.get_id(), zid=zug.get_id())
        insert_query = Template(INSERT).substitute(
                bid=bahnhof.get_id(),
                zid=zug.get_id(),
                ankunft=ankunft.strftime('%H:%M:%S'),
                erstellt=now.strftime('%Y-%m-%d %H:%M:%S'),
                aktualisiert=now.strftime('%Y-%m-%d %H:%M:%S'),
                counter=1)
        try:
            self.cursor.execute(select_query)
            if self.cursor.rowcount == 0:
                # noch kein Profileintrag vorhanden
                self.cursor.execute(insert_query)
            else:
                # Profileintrag aktualisieren
                result = self.cursor.fetchone()
                if (now.date() == result[1].date()):
                    counter = result[2]
                else:
                    counter = result[2] + 1
                update_query = Template(UPDATE).substitute(
                        aktualisiert=now.strftime('%Y-%m-%d %H:%M:%S'),
                        pid=result[0],
                        counter=counter)
                self.cursor.execute(update_query)
            self.cursor.execute(select_query)
            self.id = self.cursor.fetchone()[0]
        except MySQLdb.Error, e:
            logging.error("MySQL Error: %s", str(e))

    def get_id(self):
        """Get-Methode fuer die ID (Primary Key) des Profileintrags."""
        return self.id

    def __del__(self):
        """
        Methode fuer das Schliessen des DB Cursors, wenn das Objekt
        zerstoert wird.
        """
        self.cursor.close()
