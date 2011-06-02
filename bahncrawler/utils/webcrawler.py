import gevent
from gevent import monkey
monkey.patch_all()
import logging

from bahncrawler.strecke import Strecke
from bahncrawler.bahnhof import Bahnhof
from bahncrawler.utils.bhfparser import BhfParser
from bahncrawler.utils.conf import settings


class WebCrawler(object):

    def __init__(self):
        self.active_strecke = None
        self.current_strecke = None
        self.interval = settings['interval']

    def run(self):
        self.active_strecke = Strecke.get_latest_strecke()
        self.current_strecke = self.active_strecke
        self.start_all_parsers()
        while True:
            try:
                if (self.current_strecke == self.active_strecke):
                    logging.debug("Keine neuere Strecke gefunden")
                    gevent.sleep(self.interval)
                elif (self.current_strecke == None):
                    logging.info("Keine Strecke in der Datenbank")
                else:
                    logging.debug("Neue Strecke gefunden")
                    self.quit_all_parsers()
                    self.active_strecke = self.current_strecke
                    self.start_all_parsers()
                logging.info("Suche nach neuer Strecke")
                self.current_strecke = Strecke.get_latest_strecke()
            except KeyboardInterrupt:
                return 0

    def start_all_parsers(self):
        logging.info("Starte alle Parser")
        bhf_list = Bahnhof.get_all_for_strecke(self.active_strecke)
        # Parser-Instanzen erzeugen
        parser_list = [BhfParser(bhf) for bhf in bhf_list]
        # Jeden Parser in eigenem Thread ausfuehren
        self.jobs = [gevent.spawn(parser) for parser in parser_list]

    def quit_all_parsers(self):
        logging.info("Beende alle Parser")
        gevent.killall(self.jobs)
