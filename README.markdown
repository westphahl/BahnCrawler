Bahn Crawler
============

Praktikum Software-Engineering @ HS Ravensburg-Weingarten.
Projekt: Verspätungsstatistiken auf Strecken der Deutschen Bahn
Teilprojekt: WebCrawler zum Erfassen der Verspätungen

Hinweis: Um die Dokumentation für das gesamte Projekt einheitlich erstellen zu können, wurden Doxygen-Kommentarte anstelle von Python-Docstrings verwendet.

EXE-Datei erstellen (Windows)
-----------------------------

    $ python setup.py py2exe

Verwendung des WebCrawlers
--------------------------

    usage: bahn_crawler.py [-h] [--host HOST] [--port PORT] --user USER --password
                           PASSWORD --db DBNAME [--interval INTERVAL]
                           [--prefix PREFIX]
                           [--level {debug,info,warning,error,critical}]

    Webcrawler zum Erfassen von Verspaetungen der Bahn.

    optional arguments:
      -h, --help            show this help message and exit
      --host HOST           MySQL-Datenbank Host (default 127.0.0.1)
      --port PORT           MySQL Port (default: 3306)
      --user USER, -u USER  Benutzername fuer Datenbankverbindung
      --password PASSWORD, -p PASSWORD
                            Passwort fuer Datenbankverbindung
      --db DBNAME, -d DBNAME
                            Name der zu verwendenden Datenbank
      --interval INTERVAL, -i INTERVAL
                            Intervall fuer Pruefung auf neue Strecke
      --prefix PREFIX       Prefix fuer Datenbanktabellen
      --level {debug,info,warning,error,critical}, -l {debug,info,warning,error,critical}
                            Log Level setzen
