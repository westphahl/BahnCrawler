import logging
import MySQLdb
from string import Template

from bahncrawler.utils.conf import settings
from bahncrawler.utils.db import connection

SELECT = Template("SELECT sid from ${prefix}Strecken WHERE status = 1 " \
        "ORDER BY erstelltAm DESC LIMIT 1"
        ).safe_substitute(prefix=settings['prefix'])


## Streckenklasse fuer Zugriff auf Datenbanktabelle.
class Strecke(object):

    ## Initialisierungsmethode fuer ein Strecken-Objekt
    def __init__(self, id):
        self._status_code = 1
        self._id = id

    ## Methode fuer "==" (equal) Vergleiche.
    #
    # \param[in] obj    Zu vergleichendes Objekt
    # \return           Boolscher Wert als Ergebnis des Vergleichs
    def __eq__(self, obj):
        if (isinstance(obj, self.__class__) and (self._id == obj.get_id())):
            return True
        else:
            return False

    ## Methode fuer "!=" (not equal) Vergleiche.
    #
    # \param[in] obj    Zu vergleichendes Objekt
    # \return           Boolscher Wert als Ergebnis des Vergleichs
    def __ne__(self, obj):
        if (isinstance(obj, self.__class__) and (self._id == obj.get_id())):
            return False
        else:
            return True

    ## Klassenmethode um die neuste Strecke aus der Datenbank abzufragen.
    # 
    # \return   Strecken-Objekt fuer neuste Strecke aus der Datenbank
    @classmethod
    def get_latest_strecke(cls):
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

    ## Get-Methode fuer ID der Strecke.
    #
    # \return   ID der Strecke (Integer)
    def get_id(self):
        return self._id

    ## Set-Method um Status der Strecke zu setzen.
    #
    # \param[in] code       Status Code fuer die Strecke
    #       Gueltige Status-Codes:
    #           0 = nicht bearbeitet (d.h. noch keine Bahnhoefe angelegt)
    #           1 = ok
    #           2 = fehlerhaft
    # \param[in] message    Fehlermeldung fuer den gesetzten Status
    #
    def set_status(self, code, message):
        # TODO Status in Datenbank schreiben
        self._status_code = code
        self._status_message = message
