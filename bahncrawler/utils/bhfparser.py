import gevent
from gevent import monkey, GreenletExit
monkey.patch_all()

import logging
import re
import urllib2
from BeautifulSoup import BeautifulSoup
from datetime import datetime, date, time
from string import Template

from bahncrawler.profileintrag import Profileintrag
from bahncrawler.verspaetung import Verspaetung
from bahncrawler.zug import Zug

"""
URL-Template mit GET-Parametern zur Abfrage der Ankuenfte

Query-Parameter (alle zwingend!):
rt=1                    ->  Funktion unbekannt
input=%s                ->  UNAME des Bahnhofs
boardType=arr           ->  Ankuenfte anzeigen
time=actual             ->  momentane Zeit verwenden
productFilter=11110     ->  Bitmap (1=on/0=off)
                            | ICE | IC/EC | IR/D | NV(RB/RE) | S-Bahn |
start=yes               ->  Funktion unbekannt
"""
URL = "http://reiseauskunft.bahn.de/bin/bhftafel.exe/dn?" \
      "rt=1&" \
      "input=${uname}&" \
      "boardType=arr&" \
      "time=actual&" \
      "productsFilter=11110&" \
      "start=yes"

# Regular Expression zum Extrahieren des Zugtyp und der Nummer
ZUG_REGEX = re.compile(r'\s*(?P<typ>[A-Z]+)\s*(?P<nr>[0-9]+)\s*')


## Parser-Klasse fuer einen Bahnhof.
#
# Es wird fuer jeden Bahnhof ein eigener Bahnhof-Parser erstellt,
# welcher in bestimmten Abstaenden die Ankunfseite des Bahnhofs
# ueberprueft, analysiert und Zuege, Profileintraege sowie
# Verspaetungen erfasst und speichert.
class BhfParser:

    ## Initialisierungsmethode des Bahnhof-Parsers
    #
    # Bekommt eine Instanz eines Bahnhof-Objekts uebergeben und
    # erzeugt aus dem URL-Template eine URL fuer den Bahnhof.
    #
    # \param[in] bhf    Bahnhofs-Object fuer den Parser
    def __init__(self, bhf):
        self.bhf = bhf
        # Url aus dem Template erzeugen
        self.url = Template(URL).substitute(
                uname=urllib2.quote(self.bhf.get_uname()))

    ## Methode fuer die Darstellung der Klasse als String.
    #
    # \return   Name des Bahnhofs
    def __str__(self):
        return self.bhf.get_name()

    ## Methode welcher beim Aufruf einer Klassen-Instanz als Methode
    ## ausgefuehrt wird.
    #
    # Die Methode ist fuer die regelmaessige Ueberpruefung der Bahn-
    # hofsseite verantwortlich. Die Pruefung wird in einer Schleife
    # ausgefuehrt, wobei der Thread bis zur naechsten Zugankunft
    # wartet (sleep). In der Endlosschleife wird auch die Berechnung
    # der der Zeit bis zur naechsten Abfrage berechnet.
    # Wird der Thread beendet, so wird die Exception 'GreenletExit'
    # erzeugt und eine Statusmeldung zurueck gegeben.
    #
    # \return   Statusmeldung des Greenlets (Threads)
    def __call__(self):
        try:
            while True:
                html = self.get_html()
                current_time, late, ontime = self.parse_html(html)

                if (len(late) > 0):
                    """
                    Abfrage in 60s, wenn Verspaetungen vorhanden, da
                    Verspaetungen jederzeit verschwinden koennen.
                    Dieses Intervall bestimmt die maximale Genauigkeit mit der
                    Verspaetungen erfasst werden koennen.
                    """
                    sleep_sec = 60
                elif (len(ontime) > 0):
                    """
                    Berechnung der Zeit (in Sekunden) bis zur naechsten
                    Ankunft eines Zuges, wobei das Polling-Intervall nicht
                    kleiner als 60 Sekunden sein darf.
                    """
                    # Ankunfszeit des naechsten Zuges
                    next_arrival = ontime[0][0]
                    sleep_sec = int(
                            (next_arrival - current_time).total_seconds())
                    if (sleep_sec < 60):
                        sleep_sec = 60
                else:
                    """
                    Wenn keine Verspaetungen vorhanden und keine Ankuenfte
                    geplant sind, erfolgt das Polling im 60 Minuten Takt.
                    """
                    sleep_sec = 60 * 60

                self.log_query(late, current_time, ontime, sleep_sec)
                self.process_profileintraege(current_time, late, ontime)

                gevent.sleep(sleep_sec)
        except GreenletExit:
            return "Exit: %s" % self
        except urllib2.URLError:
            # TODO Streckenstatus auf Fehler setzen
            return "URLError: %s" % self

    ## Methode zum Abrufen des HTML-Codes.
    #
    # Die Methode oeffnet die fuer den Bahnhof erzeugte URL,
    # liest den HTML-Code aus und gibt diesen zurueck.
    #
    # \return   HTML-Code der Bahnhofs-Seite
    def get_html(self):
        response = urllib2.urlopen(self.url)
        return response.read()

    ## Methode zum Verarbeiten des HTML-Codes.
    #
    # Gibt eine Liste zurueck mit der aktuellen Zeit, verspaetete Ankuenfte
    # und geplante Ankuenfte. Verspaetete und geplante Ankuenfte sind Listen
    # und enthalten den Ankunftszeitpunkt und die Zugdaten.
    # Sind keine Ankuenfte vorhanden, werden leere Listen zurueck gegeben.
    #
    # \param[in] html   HTML-Code der Bahnhofs-Seite
    #
    # \return           Tupel mit: (aktuelle Zeit,
    #                               geplante Ankuenfte,
    #                               Verspaetungen)
    def parse_html(self, html):
        soup = BeautifulSoup(html)

        # Suche der Ankunfstabelle
        table = soup.find('table', 'result')

        if (table == None):
            """
            Rueckgabe einer leeren Ergebnisliste, wenn die Tabelle
            nicht gefunden wurde.
            Dies kann der Fall sein, wenn der Bahnhof nicht eindeutig
            ist, oder in der naechsten Zeit keine Ankuenfte geplant sind.
            """
            return (datetime.now(), [], [])

        # Alle Zeilen heraussuchen
        rows_raw = table.findAll('tr')

        # Ueberschriften und Navigations-Zeilen entfernen
        row_list = rows_raw[2:-1]

        late = []
        ontime = []
        late_flag = True

        for row in row_list:
            # Stunden und Minuten trennen und in Integer konvertieren
            h, m = row('td', 'time')[0].text.split(':')
            hour = int(h)
            minute = int(m)
            row_time = datetime.combine(
                    date.today(), time(int(hour), int(minute)))

            if (row.get('class') == 'current'):
                """
                Diese Zeile zeigt die aktuelle Zeit an.
                Alle nachfolgenden Zeilen sind keine Verspaetungen mehr.
                """
                late_flag = False
                current_time = row_time
                # Mit naechster Zeile fortfahren
                continue

            # Extrahieren von Zugtyp und Nummer
            match = ZUG_REGEX.search(row('td', 'train')[1].text)
            train_name = (match.group('typ'), match.group('nr'),)

            if late_flag:
                late.append((row_time, train_name))
            else:
                ontime.append((row_time, train_name))
        return (current_time, late, ontime)

    ## Methode zum Verarbeiten der Zuglisten.
    #
    # Es werden - falls noch nicht in der Datenbank vorhanden - Zuege,
    # Profileintraege und evtl. Verspaetungen erzeugt und gespeichert.
    #
    # \param[in] current_time   Datetime-Object mit der aktuellen Zeit
    # \param[in] late           Liste mit geplanten Ankuenften (String)
    # \param[in] ontime         Liste mit Verspaetungen (String)
    def process_profileintraege(self, current_time, late, ontime):
        for ankunft, data in ontime[0:5]:
            # Naechsten fuenf Ankuenfte im Vorraus anlegen
            typ, nr = data
            zug = Zug(typ, nr)
            Profileintrag(self.bhf, zug, ankunft)

        for ankunft, data in late:
            # Alle Verspaetungen anlegen oder aktualisieren
            typ, nr = data
            delta = self.calculate_delta(current_time, ankunft)
            zug = Zug(typ, nr)
            profil = Profileintrag(self.bhf, zug, ankunft)
            Verspaetung(profil, delta)

    ## Methode fuer die Berechnung der Zeit bis zur naechsten Ankunft
    ## bzw. der Verspaetung.
    #
    # \param[in] current_time   Datetime-Objekt mit der aktuellen Zeit
    # \param[in] train_time     Datetime-Objekt mit der Ankunftszeit eines Zuges
    #
    # \return                   Zeitdifferenz in Minuten (Betrag)
    def calculate_delta(self, current_time, train_time):
        if (current_time < train_time):
            delta = int((train_time - current_time).total_seconds() / 60)
        else:
            delta = int((current_time - train_time).total_seconds() / 60)
        return delta

    ## Methode fuer die Ausgabe von Debug- und Info-Meldungen.
    #
    # \param[in] late           Liste mit Verspaetungen (String)
    # \param[in] current_time   Datetime-Objekt mit der aktuellen Zeit
    # \param[in] ontime         Liste mit geplanten Ankuenften (String)
    # \param[in] sleep_sec      Sekunden bis zur naechsten Abfrage
    def log_query(self, late, current_time, ontime, sleep_sec):
        logging.info("Query \"%s\" (Arrivals) @ %sh",
                self.bhf.get_name(), current_time.strftime('%H:%M'))
        logging.info("Late: %s - On Time: %s - Next query in: %s sec",
                len(late), len(ontime), sleep_sec)

        next_arrival = ontime[0][0]
        next_train = ontime[0][1]
        if (len(ontime) > 0):
            logging.debug("Next arrival: %s %s @ %sh - %s min to go",
                    next_train[0],
                    next_train[1],
                    next_arrival.strftime('%H:%M'),
                    self.calculate_delta(current_time, next_arrival))

        for arrival, train in late:
            logging.debug("%s %s @ %sh - Late: %s min",
                    train[0],
                    train[1],
                    arrival.strftime('%H:%M'),
                    self.calculate_delta(current_time, arrival))
