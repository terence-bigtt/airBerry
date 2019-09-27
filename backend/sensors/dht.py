import Adafruit_DHT
import time


class DHT(object):
    def __init__(self, sensor=Adafruit_DHT.DHT22, pin=26, retries=5):
        self.pin = pin
        self.retries = retries
        self.sensor = sensor

    def get_value(self):
        hum, temp = Adafruit_DHT.read_retry(self.sensor, self.pin, retries=self.retries)
        value = {"humidity": hum, "temperature": temp, 'time': time.strftime("%d.%m.%Y %H:%M:%S"), "ts": time.time()}

        return {k: v for k, v in value.items() if v is not None}
