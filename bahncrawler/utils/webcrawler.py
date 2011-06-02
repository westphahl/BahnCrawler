import gevent
from gevent import monkey
monkey.patch_all()
import sys

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
                    gevent.sleep(self.interval)
                else:
                    self.quit_all_parsers()
                    self.active_strecke = self.current_strecke
                    self.start_all_parsers()
                print("-" * 60 )
                sys.stdout.write("WebCrawler: Suche nach neuer Strecke... ")
                self.current_strecke = Strecke.get_latest_strecke()
                sys.stdout.write("Done.\n")
            except KeyboardInterrupt:
                return 0


    def start_all_parsers(self):
        print("-" * 60)
        sys.stdout.write("WebCrawler: Starte alle Parser... ")
        bhf_list = Bahnhof.get_all_for_strecke(self.active_strecke)
        # Parser-Instanzen erzeugen
        parser_list = [BhfParser(bhf) for bhf in bhf_list]
        # Jeden Parser in eigenem Thread ausfuehren
        self.jobs = [gevent.spawn(parser) for parser in parser_list]
        sys.stdout.writelines("Done.\n")


    def quit_all_parsers(self):
        print("-" * 60)
        sys.stdout.write("WebCrawler: Beende alle Parser... ")
        gevent.killall(self.jobs)
        sys.stdout.writelines("Done.\n")

