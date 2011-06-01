class Settings(dict):

    def __init__(self):
        self.update((
            ('dbhost', '172.16.0.101'),
            ('dbport', 3306),
            ('dbuser', 'crawler'),
            ('dbpassword', 'railware'),
            ('dbname', 'swenp01'),
            ('check_interval', 60),))

    def set_from_namespace(self, ns):
        pass


settings = Settings()
