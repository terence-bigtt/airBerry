import time


class Sensors(object):
    """
    @:argument sensors: list of sensors
    """

    def __init__(self, *sensors):
        self.sensors = sensors
        self.calibrated = False

    def calibrate(self):
        for sensor in self.sensors:
            if "calibrate" in dir(sensor):
                sensor.calibrate()
        self.calibrated = True

    def get_values(self):
        values = []
        for sensor in self.sensors:
            values.append(sensor.get_value())
        return values

