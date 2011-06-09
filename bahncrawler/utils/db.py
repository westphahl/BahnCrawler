import logging
import MySQLdb
import sys

from bahncrawler.utils.conf import settings


## Klasse fuer Verbindung zur MySQL-Datenbank.
class Connection(object):

    ## Initialisierungsmethode fuer eine neue Datenbankverbindung.
    #
    # Es wird versucht eine Verbindung mit der Datenbank herzustellen.
    # Gelingt dies nicht, wird das Programm beendet.
    def __init__(self):
        try:
            self._con = MySQLdb.connect(
                    settings['host'],
                    settings['user'],
                    settings['password'],
                    settings['dbname'],
                    charset='utf8',
                    use_unicode=True)
        except MySQLdb.OperationalError, e:
            logging.error("MySQL Error: %s", str(e))
            sys.exit(1)

    ## Methode um einen neuen Cursor fuer die Datenbank zu erhalten.
    #
    # Liefert als Rueckgabewert einen neuen Datenbank-Cursor, mit welchem
    # Abfragen ausgefuehrt werden koennen. Ist keine Datenbankverbindun
    # vorhanden wird das Programm beendet.
    #
    # \return   Datenbank Cursor
    def get_cursor(self):
        try:
            return self._con.cursor()
        except MySQLdb.OperationalError, e:
            logging.error("MySQL Error: %s", str(e))
            sys.exit(1)

    ## Methode zum Schliessen der Datenbankverbindung, wenn das Objekt
    ## bei Programmende geloescht wird.
    def __del__(self):
        if hasattr(self, '_con'):
            self._con.close()


# Globale Datenbankverbindung erzeugen
connection = Connection()
