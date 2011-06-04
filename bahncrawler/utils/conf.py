class Settings(dict):
    """
    Dictionary um globale Einstellungen zu speichern.
    """

    def set_from_namespace(self, ns):
        """Einstellungen durch CLI Parameter setzen"""
        self.update(vars(ns))

# Globales Settings-Objekt erzeugen
settings = Settings()
