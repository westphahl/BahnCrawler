

class Strecke(object):

    def __init__(self):
        # TODO Status und Id aus DB lesen
        self.status_code = 1
        self.id = 1

    def __eq__(self, obj):
        if (isinstance(obj, self.__class__) and (self.id == obj.id)):
            return True
        else:
            return False

    @classmethod
    def get_latest_strecke(cls):
        return Strecke()

    def set_status(self, code, message):
        # TODO Status in Datenbank schreiben
        self.status_code = code
        self.status_message = message

    def get_status(self):
        return self.status_code
