import gevent
from gevent import monkey
monkey.patch_all()

from railware.strecke import Strecke
from railware.bahnhof import Bahnhof
from utils.bhfparser import BhfParser
from utils.db import Connection


class WebCrawler(object):

    def __init__(self, poll_int):
        self.active_strecke = None
        self.current_strecke = None
        self.intervall = poll_int

    def run(self):
        self.active_strecke = Strecke.get_latest_strecke()
        self.start_all_parsers()
        while True:
            try:
                print("-" * 50)
                print("WebCrawler: Suche nach neuer Strecke ...")
                self.current_strecke = Strecke.get_latest_strecke()
                if (self.current_strecke == self.active_strecke):
                    print("... keine neue Strecke gefunden")
                    gevent.sleep(self.intervall)
                else:
                    print("... neue Strecke gefunden")
                    self.quit_all_parsers()
                    self.active_strecke = self.current_strecke
                    self.start_all_parsers()
            except KeyboardInterrupt:
                Connection.close()
                return 0


    def start_all_parsers(self):
        print("Starte alle Parser ...")
        bhf_list = Bahnhof.get_all_for_strecke(self.active_strecke)
        # Parser-Instanzen erzeugen
        parser_list = [BhfParser(bhf) for bhf in bhf_list]
        # Jeden Parser in eigenem Thread ausfuehren
        self.jobs = [gevent.spawn(parser) for parser in parser_list]


    def quit_all_parsers(self):
        print("Beende alle Parser ...")
        gevent.killall(self.jobs)

