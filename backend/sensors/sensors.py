import time


class Sensors(object):
    """
    @:argument sensors: list of sensors
    """

    def __init__(self, *sensors):
        self.sensors = sensors
        self.calibrated = False

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
                oks.append(sensor.calibrate())
        self.calibrated = True if None not in oks else False

    def get_values(self):
        values = []
        for sensor in self.sensors:
            values.append(sensor.get_value())
        return values
