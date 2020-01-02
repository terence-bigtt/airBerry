import os
import sys
import requests
import json


class Persistor(object):
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def _send_to_url(self, datatosend):
        if type(datatosend) == list:
            for d in datatosend:
                self._send_to_url(d)
        else:
            data = datatosend
            success = False
            if self.config.url is not None:
                self.logger.info("will try to send to url")
                try:
                    json = data.copy()
                    ts = json.pop("ts")
                    js={"ts":ts, "values":json}
                    self.logger.info(js)
                    r= requests.post(self.config.url, json=js)
                    self.logger.info(r.status_code)
                    if(r.status_code >=300):
                        self.logger.error(r.content)
                        success=False
                    else:
                        success = True
                except Exception as e:
                    self.logger.error("failed sending to url")
                    self.logger.error(e.args)

            self._handle_temp(success, data)

    def _handle_temp(self, success, data):
        filename = os.path.join(self.config.fullpath, "temp_data.jsonl")
        if not success:
            if os.path.exists(filename): mode="a"
            else: mode="w"
            with open(filename, mode) as f:
                f.write(json.dumps(data) + "\n")
        if success:
            logger.info("successfully sent last measurement, will send local")
            if os.path.exists(filename):
                with open(filename, "r") as f:
                    logger.info("readin previous temp data")
                    datae = [json.loads(line) for line in f.readlines()]
            logger.info("remove temp data")
            os.remove(filename)
            for i, data in enumerate(datae):
                self.logger.info(f"send data {i} to url.")
                self._send_to_url(data)

    def _to_disk(self, newdata):
        filename = os.path.join(self.config.fullpath, self.config.buffer_name)
        data = self.read_buffer()
        data = [newdata] + data[:self.config.data_buffer - 1]
        with open(filename, "w+") as f:
            f.write("\n".join([json.dumps(d) for d in data]) + "\n")

    def persist(self, data):
        try:
            self.logger.info("send to url")
            self._send_to_url(data)
        except Exception as e:
            self.logger.error(e.args)
        try:
            self.logger.info("persist to disk")
            self._to_disk(data)
        except Exception as e:
            self.logger.error("failed persist to disk")
            self.logger.error(e.args)

    def read_buffer(self):
        data = []
        filename = os.path.join(self.config.fullpath, self.config.buffer_name)
        if os.path.exists(filename):
            with open(filename, "r") as f:
                lines = f.readlines()
            data = []
            for i, line in enumerate(lines):
                try:
                    data.append(json.loads(line))
                except Exception as e:
                    self.logger.error("failed to read line {i}")
                    self.logger.error(e.args)
        return data
