import random
import time


class DummySensor(object):
    def __init__(self):
        self.calib = False

    def get_value(self):
        value = random.randint(10, 20)
        ts = time.time()
        tstime = time.strftime("%d.%m.%Y %H:%M:%S")
        return dict(ts=ts, time=tstime, dummy=value)

    def calibrate(self):
        self.calib=True