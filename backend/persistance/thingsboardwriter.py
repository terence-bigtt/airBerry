from persistance.postwriter import PostWriter, WritePost
from sensors.sensors import Measure
from pykka import ThreadingActor


class TBWriter(ThreadingActor):
    def __init__(self, base_url, token, tempfile, logger):
        ThreadingActor.__init__(self)
        self.url = f"{base_url}/api/v1/{token}/telemetry"
        self.data_format = """{{ "ts":{ts}, "values":{{ "{name}":{value} }} }}"""
        self.postactor = PostWriter.start(self.url, tempfile, logger)

    def on_receive(self, message):
        if type(message) == Measure:
            data = message.format(self.data_format).copy()
            ts = data.get('ts') * 1000
            data.update({'ts': ts})
            return self.postactor.ask(WritePost(data))

    def on_stop(self):
        self.postactor.stop()
