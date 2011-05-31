class Bahnhof(object):

    def __init__(self, name, strecke):
        self.name = name
        self.strecke = strecke
        # TODO aus Datenbenk:
        # self.id 

    def get_name(self):
        return self.name

    def get_strecke(self):
        return self.strecke

    @classmethod
    def get_all_for_strecke(cls, strecke):
        namen_list = [
                u"Stuttgart Hbf",
                u"Tuebingen Hbf",
                u"Sigmaringen",
                u"Friedrichshafen",
                u"Lindau Hbf",
                u"Memmingen",
                u"NichtExistenterBahnhof",
        ]

        bahnhof_list = [Bahnhof(name, strecke) for name in namen_list]
        return bahnhof_list
