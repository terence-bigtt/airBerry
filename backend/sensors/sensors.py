import time, datetime, json
from pykka import ThreadingActor
from typing import List

class Measure(object):
    def __init__(self, name, value, ts, time_format="%d.%m.%Y %H:%M:%S", **kw):
        self.ts = ts
        self.time = datetime.datetime.fromtimestamp(ts).strftime(time_format)
        self.name = name
        self.value = value

    def format(self, format_string=None):
        if format_string is None:
            return self.__dict__
        else:
            return json.loads(format_string.format(**self.__dict__))

    def to_string(self):
        return json.dumps(self.format())

    @staticmethod
    def from_dict(d):
        return Measure(**d)

    @staticmethod
    def from_string(s):
        return Measure(**json.loads(s))


class SensorsMessages(object):
    CALIBRATE = "CALIBRATE"
    CALIBRATION_HISTORY = "CALIBRATION_HISTORY"
    READ = "READ"


class Sensors(ThreadingActor):
    """
    @:argument sensors: list of sensors each sensor must implement get_value() and return an object containing
    {'ts': timestamp, <name1>: <value1>, <name2>: <value2>, ...}
    """

    def __init__(self,logger, *sensors, timeformat="%d.%m.%Y %H:%M:%S"):
        ThreadingActor.__init__(self)
        self.sensors = sensors
        self.logger=logger
        self.timeformat = timeformat
        self.calibrated = False

    def on_receive(self, message):
        if message == SensorsMessages.CALIBRATE:
            return self.calibrate()
        if message == SensorsMessages.CALIBRATION_HISTORY:
            return self.calibration_history()
        if message == SensorsMessages.READ:
            return self.get_values()

    def calibration_history(self):
        cals = []
        for sensor in self.sensors:
            if "calibration_history" in dir(sensor):
                cals.extend(sensor.calibration_history)
        return cals

    def calibrate(self):
        oks = []
        for sensor in self.sensors:
            if "calibrate" in dir(sensor):
                self.logger.info("Calibrate sensor {}".format(sensor))
                oks.append(sensor.calibrate())
        self.calibrated = True if None not in oks else False
        return self.calibrated

    def get_values(self) -> List[Measure]:
        values = []
        for sensor in self.sensors:
            try:
                values.append(sensor.get_value())
            except Exception as e:
                self.logger.error(e.args)
                pass
        measures = []
        for v in values:
            measures.extend(self._raw_to_measures(v))
        return measures

    def _raw_to_measures(self, value):
        val = value.copy()
        ts = val.pop("ts")
        return [Measure(k, v, ts, self.timeformat) for k, v in val.items() if k != 'time']
