import gevent
from gevent import monkey
monkey.patch_all()

import logging

from bahncrawler.bahnhof import Bahnhof
from bahncrawler.strecke import Strecke
from bahncrawler.utils.bhfparser import BhfParser
from bahncrawler.utils.conf import settings


class WebCrawler(object):
    """
    Webcrawler welcher fuer die Abfrage von Strecken sowie das Starten der
    Parser fuer die zugehoerigen Bahnhoefe verantwortlich ist.
    """

    def __init__(self):
        """Initialisierungsmethode fuer den WebCrawler"""
        self.active_strecke = None
        self.current_strecke = None
        self.jobs = []
        self.interval = settings['interval']

    def run(self):
        """
        Methode zum Ausfuehren des Crawler-Supervisors.

        In festen Zeitabstaenden wird die Datenbank auf neue Strecken
        geprueft und die zugehoerigen Bahnhofsparser gestartet und
        vorher beendet, falls momentan bereits eine andere Strecke
        bearbeitet wird.

        Wird der WebCrawler mit CTRL+C beendet, so wird die Exception
        "KeyboardInterrupt" abgefangen und die Parser und das Programm
        beendet.
        """
        self.active_strecke = Strecke.get_latest_strecke()
        self.current_strecke = self.active_strecke
        self.start_all_parsers()

        while True:
            try:
                if (self.current_strecke != self.active_strecke):
                    logging.debug("Neue Strecke gefunden")
                    self.quit_all_parsers()
                    self.active_strecke = self.current_strecke
                    self.start_all_parsers()
                gevent.sleep(self.interval)
                logging.info("Suche nach neuer Strecke")
                self.current_strecke = Strecke.get_latest_strecke()
            except KeyboardInterrupt:
                self.quit_all_parsers()
                return 0

    def start_all_parsers(self):
        """
        Methode zum Starten der Bahnhofsparser.

        Es wird fuer jeden Bahnhof der aktiven Strecke ein Parser
        erzeugt und gestartet. Die Parser werden in einem eigenen
        Greenlet (Thread) ausgefuehrt.
        """
        if self.active_strecke == None:
            return
        logging.info("Starte alle Parser")
        bhf_list = Bahnhof.get_all_for_strecke(self.active_strecke)
        # Parser-Instanzen erzeugen
        parser_list = [BhfParser(bhf) for bhf in bhf_list]
        # Jeden Parser in eigenem Thread ausfuehren
        self.jobs = [gevent.spawn(parser) for parser in parser_list]

    def quit_all_parsers(self):
        """
        Methode zum Beenden der Banhofsparser.
        """
        logging.info("Beende alle Parser")
        gevent.killall(self.jobs)
        self.jobs = []
