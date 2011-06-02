#!/usr/bin/env python

import sys
import logging
import argparse

from bahncrawler.utils.conf import settings


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Webcrawler zum Erfassen von Verspaetungen der Bahn.")

    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default=3306, type=int)
    parser.add_argument('--user', '-u', required=True)
    parser.add_argument('--password', '-p', required=True)
    parser.add_argument('--db', '-d', required=True, dest='dbname')
    parser.add_argument('--interval', '-i', default=60, type=int)
    parser.add_argument('--prefix', default='')
    parser.add_argument('--level', '-l', default='info',
            choices=['debug', 'info', 'warning', 'error', 'critical',],
            help="set the log level")

    ns = parser.parse_args()
    settings.set_from_namespace(ns)
    logging.basicConfig(
            format='%(levelname)s:%(module)s: %(message)s',
            level=settings['level'].upper())

    from bahncrawler.utils.webcrawler import WebCrawler
    c = WebCrawler()
    sys.exit(c.run())
