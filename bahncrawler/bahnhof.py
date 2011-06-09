import logging
import MySQLdb
from string import Template

from bahncrawler.utils.conf import settings
from bahncrawler.utils.db import connection

SELECT = Template("SELECT bid, name, uname FROM ${prefix}Bahnhoefe " \
        "WHERE sid_fk = ${sid}").safe_substitute(prefix=settings['prefix'])


## Bahnhofsklasse fuer Zugriff auf DB-Tabelle.
class Bahnhof(object):

    ## Initialisierungsmethode fuer einen Bahnhof.
    #
    # Bei Instanziierung eines Bahnhofs-Objektes wird kein Eintrag
    # in der Datenbank erzeugt.
    #
    # \param[in] id         Id des Bahnhofs
    # \param[in] name       Name des Bahnhofs
    # \param[in] uname      Eindeutiger Name des Bahnhofs
    # \param[in] strecke    Strecken-Objekt fuer die Zuordnung
    def __init__(self, id, name, uname, strecke):
        self._id = id
        self._name = name
        self._uname = uname
        self._strecke = strecke

    ## Get-Methode fuer Namen des Bahnhofs.
    #
    # \return   Name des Bahnhofs
    def get_name(self):
        return self._name

    ## Get-Methode fuer "Unique Name" des Bahnhofs.
    #
    # \return   Eindeutiger Name des Bahnhofs
    def get_uname(self):
        return self._uname

    ## Get-Methode fuer ID (Primary Key) des Bahnhofs.
    #
    # \return   Id des Bahnhofs (Integer)
    def get_id(self):
        return self._id

    ## Klassenmethod um alle Bahnhoefe einer bestimmten Strecke aus der
    ## Datenbank auszulesen.
    #
    # Die Methode bekommt ein Streckenobjekt uebergeben und liefert eine
    # Liste mit Bahnhofs-Objekten zurueck.
    #
    # \param[in] strecke    Strecken-Object fuer welchen Bahnhoefe
    #                       abgefragt werden
    #
    # \return               Liste von Bahnhofs-Objekten
    @classmethod
    def get_all_for_strecke(cls, strecke):
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
