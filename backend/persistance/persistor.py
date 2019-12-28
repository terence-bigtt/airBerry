import os
import requests
import json


class Persistor(object):
    def __init__(self, config):
        self.config = config

    def _send_to_url(self, datatosend):
        if type(datatosend) == list:
            for d in datatosend:
                self._send_to_url(d)
        else:
            data = datatosend
            success = False
            if self.config.url is not None:
                print("will try to send to url")
                try:
                    r= requests.post(self.config.url, json=data)
                    print(r.status_code)
                    if(r.status_code >=300):
                        print(r.content)
                    success = True
                except Exception as e:

                    print(e.args)

            self._handle_temp(success, data)

    def _handle_temp(self, success, data):
        filename = os.path.join(self.config.fullpath, "temp_data.jsonl")
        if not success:
            with open(filename, "a") as f:
                f.write(json.dumps(data) + "\n")
        if success:
            if os.path.exists(filename):
                with open(filename, "r") as f:
                    datae = [json.loads(line) for line in f.readlines()]
            os.remove(filename)
            for data in datae:
                self._send_to_url(data)

    def _to_disk(self, newdata):
        filename = os.path.join(self.config.fullpath, self.config.buffer_name)
        data = self.read_buffer()
        data = [newdata] + data[:self.config.data_buffer - 1]
        with open(filename, "w+") as f:
            f.write("\n".join([json.dumps(d) for d in data]) + "\n")

    def persist(self, data):
        try:
            print("send to url")
            self._send_to_url(data)
        except Exception as e:
            print(e.args)
        try:
            print("persist to disk")
            self._to_disk(data)
        except Exception as e:
            print(e.args)

    def read_buffer(self):
        data = []
        filename = os.path.join(self.config.fullpath, self.config.buffer_name)
        if os.path.exists(filename):
            with open(filename, "r") as f:
                lines = f.readlines()
            data = [json.loads(line) for line in lines]
        return data
