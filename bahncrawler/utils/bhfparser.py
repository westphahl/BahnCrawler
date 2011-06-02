import gevent
from gevent import monkey, GreenletExit
monkey.patch_all()

import re
import urllib2
from urllib2 import URLError
from datetime import datetime, date, time
from BeautifulSoup import BeautifulSoup

from bahncrawler.zug import Zug
from bahncrawler.profileintrag import Profileintrag
from bahncrawler.verspaetung import Verspaetung

"""
URL-Templage mit GET-Parametern zur Abfrage der Ankuenfte

Query-Parameter (alle zwingend!):
rt=1                    ->  Funktion unbekannt
input=%s                ->  UID des Bahnhofs
boardType=arr           ->  Ankuenfte anzeigen
time=actual             ->  momentane Zeit verwenden
productFilter=11110     ->  Bitmap (1=on/0=off)
                            | ICE | IC/EC | IR/D | NV(RB/RE) | S-Bahn |
start=yes               ->  Funktion unbekannt
"""
URL_TEMPLATE = "http://reiseauskunft.bahn.de/bin/bhftafel.exe/dn?" +\
        "rt=1&" +\
        "input=%s&" +\
        "boardType=arr&" +\
        "time=actual&" +\
        "productsFilter=11110&" +\
        "start=yes"

ZUG_REGEX = re.compile(r'\s*(?P<typ>[A-Z]+)\s*(?P<nr>[0-9]+)\s*')


class BhfParser:
    """
    Parser-Klasse fuer einen Bahnhof.

    Es wird fuer jeden Bahnhof ein eigener Bahnhof-Parser erstellt,
    welcher in bestimmten Abstaenden die Ankunfseite des Bahnhofs
    ueberprueft, analysiert und Zuege, Profileintraege sowie
    Verspaetungen erfasst und speichert.
    """

    def __init__(self, bhf):
        """
        Initialisierungsmethode des Bahnhof-Parsers

        Bekommt eine Instanz eines Bahnhof-Objekts uebergeben und
        erzeugt aus dem URL-Template eine URL fuer den Bahnhof.
        """
        self.bhf = bhf
        # Url aus dem Template erzeugen
        self.url = URL_TEMPLATE % urllib2.quote(self.bhf.get_uname())

    def __str__(self):
        """
        Methode fuer die Darstellung der Klasse als String.
        
        Gibt den Namen des Bahnhofs zurueck
        """
        return self.bhf.get_name()

    def __call__(self):
        """
        Methode welcher beim Aufruf einer Klassen-Instanz als Methode
        ausgefuehrt wird.

        Die Methode ist fuer die regelmaessige Ueberpruefung der Bahn-
        hofsseite verantwortlich. Die Pruefung wird in einer Schleife
        ausgefuehrt, wobei der Thread bis zur naechsten Zugankunft
        wartet (sleep).
        In der Endlosschleife wird auch die Berechnung der der Zeit bis
        zur naechsten Abfrage berechnet.
        Wird der Thread beendet, so wird die Exception 'GreenletExit'
        erzeugt und eine Statusmeldung zurueck gegeben.
        """
        try:
            while True:
                html = self.get_html()
                current_time, late, ontime = self.parse_html(html)

                if (len(late) > 0):
                    """
                    Abfrage in 60s, wenn Verspaetungen vorhanden, da Verspaetungen
                    jederzeit verschwinden koennen.
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
                    sleep_sec = int((next_arrival - current_time).total_seconds())
                    if (sleep_sec < 60):
                        sleep_sec = 60
                else:
                    """
                    Wenn keine Verspaetungen vorhanden und keine Ankuenfte
                    geplant sind, erfolgt das Polling im 60 Minuten Takt.
                    """
                    sleep_sec = 60*60

                # TODO >>> debug
                self.print_debug(late, current_time, ontime, sleep_sec)
                # TODO <<<
                
                self.process_profileintraege(current_time, late, ontime)

                gevent.sleep(sleep_sec)
        except GreenletExit:
            return "Exit: %s" % self
        except URLError:
            # TODO Streckenstatus auf Fehler setzen
            return "URLError: %s" % self

    def get_html(self):
        """
        Methode zum Abrufen des HTML-Codes.

        Die Methode oeffnet die fuer den Bahnhof erzeugte URL und
        liest den HTML-Code aus und gibt diesen zurueck.
        """
        response = urllib2.urlopen(self.url)
        return response.read()

    def parse_html(self, html):
        """
        Methode zum Verarbeiten des HTML-Codes.

        """
        soup = BeautifulSoup(html)

        # Suche der Ankunfstabelle
        table = soup.find('table', 'result')

        if (table == None):
            """
            Rueckgabe einer leeren Ergebnisliste, wenn die Tabelle
            nicht gefunden wurde.
            Dies kann der Fall sein, wenn der Name des Bahnhofs nicht eindeutig
            ist, oder in der naechsten Zeit keine Ankuenfte vorhanden sind.
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
                Alle nachfolgenden Zeilen sind keine Verspaetungen mehr,
                darum Flag setzten und die aktuelle Zeit speichern.
                """
                late_flag = False
                current_time = row_time
                # Mit naechster Zeile fortfahren
                continue

            match = ZUG_REGEX.search(row('td', 'train')[1].text)
            train_name = (match.group('typ'), match.group('nr'),)
            if late_flag:
                late.append((row_time, train_name))
            else:
                ontime.append((row_time, train_name))
        return (current_time, late, ontime)

    def process_profileintraege(self, current_time, late, ontime):
        for ankunft, data in ontime[0:5]:
            typ, nr = data
            zug = Zug(typ, nr)
            Profileintrag(self.bhf, zug, ankunft)

        for ankunft, data in late:
            typ, nr = data
            delta = int((current_time - ankunft).total_seconds() / 60)
            zug = Zug(typ, nr)
            profil = Profileintrag(self.bhf, zug, ankunft)
            Verspaetung(profil, delta)

    # TODO >>> debug
    def print_debug(self, late, current_time, ontime, sleep_sec):
        print("-" * 60)
        print("> %s (Arrivals) @ %sh" %
                (self.bhf.get_name(), current_time.strftime('%H:%M')))
        print("Late: %s - On Time: %s - Next query in: %s sec" %
                (len(late), len(ontime), sleep_sec))
        if (len(ontime) > 0):
            print("Next arrival: %s @ %sh - %s min to go" % (
            ontime[0][1],
            ontime[0][0].strftime('%H:%M'),
            int((ontime[0][0]- current_time).total_seconds() / 60)))
        for arrival, train in late:
            print("%s @ %sh - Late: %s min" % (
                train,
                arrival.strftime('%H:%M'),
                int((current_time - arrival).total_seconds() / 60)))
    # TODO <<<
