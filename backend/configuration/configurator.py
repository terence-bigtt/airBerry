import os, yaml


class Configurator(object):
    def __init__(self, directory=".airberry"):
        self.url_pattern = None
        self.token = None
        self.url = None
        self.directory = directory
        self.home = os.environ.get("HOME")
        self.data_buffer = None
        self.buffer_name = None
        self.period_s = None
        self.home = os.environ.get("HOME")
        self.fullpath = os.path.join(self.home, self.directory)
        self.fullpath = os.path.join(self.home, self.directory)
        self.configfile = os.path.join(self.fullpath, "configuration.yaml")
        self._create_directory()
        self.read()

    def _create_directory(self):
        os.makedirs(self.fullpath, exist_ok=True)

    def read(self):
        config = {}
        print(self.configfile)
        if os.path.exists(self.configfile):

            with open(self.configfile, "r") as f:
                config = yaml.load(f)

        self.url_pattern = config.get("url_pattern")
        self.token = config.get('token')
        url_frompattern = None
        if self.url_pattern is not None and self.token is not None :
            url_frompattern= self.url_pattern.format(self.token)
        self.url = config.get("url", url_frompattern)
        self.buffer_name = config.get("buffername", "telemetry_tmp.jsonl")
        self.data_buffer = config.get("data_buffer", 100)
        self.period_s = config.get("period_s",  60)
        return config

    def update(self, config, write=True):
        fields = ["url_pattern", "token", "url", "buffer_name", "period_s"]
        for k, v in config.items():
            if k in fields:
                setattr(self, k, v)
        if self.url_pattern is not None and self.token is not None :
            url_frompattern= self.url_pattern.format(self.token)
        self.url = config.get("url", url_frompattern)
        if write:
            return self.write()
        return config

    def write(self):
        config = {
            "url_pattern": self.url_pattern,
            "token": self.token,
            "url": self.url,
            "buffer_name": self.buffer_name,
            "data_buffer": self.data_buffer,
            "period_s": self.period_s
        }

        with open(self.configfile, "w") as f:
            yaml.dump(config, f)
        return config
