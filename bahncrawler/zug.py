import MySQLdb
import logging
from string import Template

from bahncrawler.utils.conf import settings
from bahncrawler.utils.db import connection

INSERT = Template("INSERT INTO ${prefix}Zuege (typ, nummer) VALUES ('${typ}', '${nummer}')").safe_substitute(prefix=settings['prefix'])
SELECT = Template("SELECT zid, typ, nummer FROM ${prefix}Zuege WHERE typ = '${typ}' AND nummer = '${nummer}'").safe_substitute(prefix=settings['prefix'])


class Zug(object):

    def __init__(self, typ, nr):
        self.cursor = connection.get_cursor()
        select_query = Template(SELECT).substitute(typ=typ, nummer=nr)
        insert_query = Template(INSERT).substitute(typ=typ, nummer=nr)
        try:
            self.cursor.execute(select_query)
            if self.cursor.rowcount == 0:
                self.cursor.execute(insert_query)
            self.cursor.execute(select_query)
            self.id, self.typ, self.nr = self.cursor.fetchone()
        except MySQLdb.Error, e:
            logging.error("MySQL Error: %s", str(e))

    def get_id(self):
        return self.id

    def __del__(self):
        self.cursor.close()
