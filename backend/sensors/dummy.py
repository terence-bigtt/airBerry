import os, json, time, random


class DummySensor(object):
    def __init__(self, caldir=".", name="dummy"):
        self.calib = False
        self.name=name
        self.calibration_history = []
        self.calibration = {}
        self._caldir = caldir
        self._calfile = "dummy.jsonl"
        self._read_calibration_data()

    def get_value(self):
        value = random.randint(10, 20)
        ts = time.time()
        tstime = time.strftime("%d.%m.%Y %H:%M:%S")
        return {'ts':ts, 'time':tstime, self.name:value}

    def calibrate(self):
        self._write_calibration_data()
        self.calib = True

    def _read_calibration_data(self):
        try:
            with open(os.path.join(self._caldir, self._calfile), 'r') as f:
                self.calibration_history = [json.loads(line) for line in f.readlines()]
            self.calibration = self.calibration_history[-1]
        except:
            self.calibration_history = []
            self.calibration = {}

    def _write_calibration_data(self):
        with open(os.path.join(self._caldir, self._calfile), 'a+') as f:
            data = {'ts': time.time(), 'dummy': 'dummy', 'device': "dummy"}
            f.write(json.dumps(data) + '\n')
            self.calibration_history.append(data)
            self.calibration = data
