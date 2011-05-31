#!/usr/bin/env python

import sys
from utils.webcrawler import WebCrawler

# Polling Intervall fuer die Pruefung auf neue Strecke
INTERVALL_STRECKE = 60

if __name__ == '__main__':
    wc = WebCrawler(INTERVALL_STRECKE)
    sys.exit(wc.run())
