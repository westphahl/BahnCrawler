#!/usr/bin/env python

"""
Autor: Simon Westphahl

Usage: bahn_crawler.py [-h] [--host HOST] [--port PORT] --user USER --password
                       PASSWORD --db DBNAME [--interval INTERVAL]
                       [--prefix PREFIX]
                       [--level {debug,info,warning,error,critical}]

Webcrawler zum Erfassen von Verspaetungen der Bahn.

Arguments:
  -h, --help                        Hilfe anzeigen
  --host HOST                       MySQL-Datenbank Host (default 127.0.0.1)
  --port PORT                       MySQL Port (default: 3306)
  --user USER, -u USER              Benutzername fuer Datenbankverbindung
  --password PASSWORD, -p PASSWORD  Passwort fuer Datenbankverbindung
  --db DBNAME, -d DBNAME            Name der zu verwendenden Datenbank
  --interval INTERVAL, -i INTERVAL  Intervall fuer Pruefung auf neue Strecke
  --prefix PREFIX                   Prefix fuer Datenbanktabellen
  --level {debug,info,warning,error,critical}, -l {debug,info,warning,error,critical}
                                    Log Level setzen
"""

import sys
import logging
import argparse

from bahncrawler.utils.conf import settings


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Webcrawler zum Erfassen von Verspaetungen der Bahn.")

    parser.add_argument('--host', default='127.0.0.1',
            help="MySQL-Datenbank Host (default 127.0.0.1)")
    parser.add_argument('--port', default=3306, type=int,
            help="MySQL Port (default: 3306)")
    parser.add_argument('--user', '-u', required=True,
            help="Benutzername fuer Datenbankverbindung")
    parser.add_argument('--password', '-p', required=True,
            help="Passwort fuer Datenbankverbindung")
    parser.add_argument('--db', '-d', required=True, dest='dbname',
            help="Name der zu verwendenden Datenbank")
    parser.add_argument('--interval', '-i', default=60, type=int,
            help="Intervall fuer Pruefung auf neue Strecke")
    parser.add_argument('--prefix', default='',
            help="Prefix fuer Datenbanktabellen")
    parser.add_argument('--level', '-l', default='info',
            choices=['debug', 'info', 'warning', 'error', 'critical',],
            help="Log Level setzen")

    # Argumente verarbeiten
    ns = parser.parse_args()
    # Einstellungen setzen
    settings.set_from_namespace(ns)
    # Logging Format
    logging.basicConfig(
            format='%(levelname)s:%(module)s: %(message)s',
            level=settings['level'].upper())

    # WebCrawler erzeugen und starten
    from bahncrawler.utils.webcrawler import WebCrawler
    c = WebCrawler()
    sys.exit(c.run())
