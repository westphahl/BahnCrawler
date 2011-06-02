class Settings(dict):

    def set_from_namespace(self, ns):
        self.update(vars(ns))


settings = Settings()
