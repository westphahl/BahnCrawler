from datetime import datetime


class Profileintrag(object):

    def __init__(self, bahnhof, zug, ankunft):
        self.bahnhof = bahnhof
        self.zug = zug
        self.ankunft = ankunft
        self.hinzugefuegt = datetime.now()
        self.letzte_abfrage = self.hinzugefuegt
        sql = """INSERT INTO  `swenp_wydler`.`test_Profileintraege` (
            `pid`, `bid_fk`, `zid_fk`, `geplanteAnkunft`, `erstelltAm`,
            `aktualisiertAm`) VALUES (
            )"""

    @classmethod
    def get_profileintrag(cls, bahnhof, zug, ankunft):
        return Profileintrag(bahnhof, zug, ankunft)

    def update_profileintrag(self):
        self.letzte_abfrage = datetime.now()
