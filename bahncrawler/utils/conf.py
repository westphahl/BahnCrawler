## Dictionary um globale Einstellungen zu speichern.
class Settings(dict):

    ## Einstellungen durch CLI Parameter setzen.
    #
    # \param[in] ns     Namespace-Object von "argparse"
    def set_from_namespace(self, ns):
        self.update(vars(ns))

# Globales Settings-Objekt erzeugen
settings = Settings()
