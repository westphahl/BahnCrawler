class Verspaetung(object):

    def __init__(self, profil_eintrag, verspaetung):
        self.profil_eintrag = profil_eintrag
        self.verspaetung = verspaetung
        # TODO aus Datenbenk:
        # self.id 

    def update_verspaetung(self, verspaetung):
        self.verspaetung = verspaetung

    @classmethod
    def get_verspaetung(cls, profil_eintrag):
        return Verspaetung(profil_eintrag, 0)
