from pykka import ThreadingActor
from persistance.diskwriter import DiskWriter, DiskWriterMessages
import requests


# TODO: Write Message classes
# TODO: write ThingsBoard writer
# TODO: write post with mock server


class WritePost(object):
    def __init__(self, data, headers={}):
        self.data = data
        self.headers = headers


class PostWriter(ThreadingActor):
    def __init__(self, url, tempfilepath, logger):
        ThreadingActor.__init__(self)
        self.url = url
        self.logger = logger
        self.diskwriter = DiskWriter.start(tempfilepath, -1, logger)

    def on_receive(self, message):
        if type(message) == WritePost:
            return self._send_to_url(message.data, message.headers)

    def _send_to_url(self, data, header={}):
        success = False
        if type(data) == list:
            successes = []
            for d in data:
                self._send_to_url(d)
        else:
            data = data
            success = False
            if self.url is not None:
                self.logger.info(f"will try to post to {self.url}")
                try:
                    r = requests.post(self.url, json=data, headers=header, verify=False)
                    self.logger.info(r.status_code)
                    if r.status_code >= 300:
                        self.logger.error(r.content)
                        success = False
                    else:
                        success = True
                except Exception as e:
                    self.logger.error("failed sending to url")
                    self.logger.error(e.args)

            self._handle_temp(success, data)
        return success

    def _handle_temp(self, success, data):
        if not success:
            self.diskwriter.ask(DiskWriterMessages.Write(data))
        if success:
            self.logger.info("successfully sent last measurement, will send previous temporary data")
            tosend = self.diskwriter.ask(DiskWriterMessages.POP)
            if tosend is not None:
                self._send_to_url(tosend)
