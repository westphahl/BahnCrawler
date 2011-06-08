import logging
import MySQLdb
import sys

from bahncrawler.utils.conf import settings


class Connection(object):
    """Klasse fuer Verbindung zur MySQL-Datenbank."""

    def __init__(self):
        """
        Initialisierungsmethode fuer eine neue Datenbankverbindung.

        Es wird versucht eine Verbindung mit der Datenbank herzustellen.
        Gelingt dies nicht, wird das Programm beendet.
        """
        try:
            self.con = MySQLdb.connect(
                    settings['host'],
                    settings['user'],
                    settings['password'],
                    settings['dbname'],
                    charset='utf8',
                    use_unicode=True)
        except MySQLdb.OperationalError, e:
            logging.error("MySQL Error: %s", str(e))
            sys.exit(1)

    def get_cursor(self):
        """
        Methode um einen neuen Cursor fuer die Datenbank zu erhalten.

        Liefert als Rueckgabewert einen neuen Datenbank-Cursor, mit welchem
        Abfragen ausgefuehrt werden koennen. Ist keine Datenbankverbindun
        vorhanden wird das Programm beendet.
        """
        try:
            return self.con.cursor()
        except MySQLdb.OperationalError, e:
            logging.error("MySQL Error: %s", str(e))
            sys.exit(1)

    def __del__(self):
        """
        Methode zum Schliessen der Datenbankverbindung, wenn das Objekt
        bei Programmende geloescht wird.
        """
        if hasattr(self, 'con'):
            self.con.close()


# Globale Datenbankverbindung erzeugen
connection = Connection()
