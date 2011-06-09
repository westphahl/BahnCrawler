import gevent
from gevent import monkey
monkey.patch_all()

import logging

from bahncrawler.bahnhof import Bahnhof
from bahncrawler.strecke import Strecke
from bahncrawler.utils.bhfparser import BhfParser
from bahncrawler.utils.conf import settings


## Webcrawler welcher fuer die Abfrage von Strecken sowie das Starten der
## Parser fuer die Bahnhoefe verantwortlich ist.
class WebCrawler(object):

    ## Initialisierungsmethode fuer den WebCrawler
    def __init__(self):
        self._active_strecke = None
        self._current_strecke = None
        self._jobs = []
        self._interval = settings['interval']

    ## Methode zum Ausfuehren des Crawler-Supervisors.
    #
    # In festen Zeitabstaenden wird die Datenbank auf neue Strecken
    # geprueft und die zugehoerigen Bahnhofsparser gestartet und
    # vorher beendet, falls momentan bereits eine andere Strecke
    # bearbeitet wird.
    # 
    # Wird der WebCrawler mit CTRL+C beendet, so wird die Exception
    # "KeyboardInterrupt" abgefangen und die Parser und das Programm
    # beendet.
    def run(self):
        self._active_strecke = Strecke.get_latest_strecke()
        self._current_strecke = self._active_strecke
        self.start_all_parsers()

        while True:
            try:
                if (self._current_strecke != self._active_strecke):
                    logging.debug("Neue Strecke gefunden")
                    self.quit_all_parsers()
                    self._active_strecke = self._current_strecke
                    self.start_all_parsers()
                gevent.sleep(self._interval)
                logging.info("Suche nach neuer Strecke")
                self._current_strecke = Strecke.get_latest_strecke()
            except KeyboardInterrupt:
                self.quit_all_parsers()
                return 0

    ## Methode zum Starten der Bahnhofsparser.
    #
    # Es wird fuer jeden Bahnhof der aktiven Strecke ein Parser
    # erzeugt und gestartet. Die Parser werden in einem eigenen
    # Greenlet (Thread) ausgefuehrt.
    def start_all_parsers(self):
        if self._active_strecke == None:
            return
        logging.info("Starte alle Parser")
        bhf_list = Bahnhof.get_all_for_strecke(self._active_strecke)
        # Parser-Instanzen erzeugen
        parser_list = [BhfParser(bhf) for bhf in bhf_list]
        # Jeden Parser in eigenem Thread ausfuehren
        self._jobs = [gevent.spawn(parser) for parser in parser_list]

    ## Methode zum Beenden der Banhofsparser.
    def quit_all_parsers(self):
        logging.info("Beende alle Parser")
        gevent.killall(self._jobs)
        self._jobs = []
