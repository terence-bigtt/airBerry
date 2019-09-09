import adafruit_mcp3xxx.mcp3008 as MCP
import board
import busio
import digitalio
from adafruit_mcp3xxx.analog_in import AnalogIn
import time
import math


class MqResponse(object):
    def __init__(self):
        self._nh4pars = [(10, 2.6), (100, 1)]
        self._copars = [(10, 2.9), (100, 1.5)]
        self._co2pars = [(10, 2.15), (100, 1.1)]
        self.nh4 = self._power_law(self._nh4pars)
        self.co = self._power_law(self._copars)
        self.co2 = self._power_law(self._co2pars)
        self.laws = {MqGaz.NH4: self.nh4, MqGaz.CO: self.co, MqGaz.CO2:self.co2}

    def _power_law(self, pars):
        exponent = math.log(pars[1][1] / pars[0][1]) / math.log(pars[1][0] / pars[0][0])
        return lambda x: pars[0][1] * math.pow((x / pars[0][0]), exponent)


class MqGaz:
    NH4 = 0
    CO = 1
    CO2 = 2

    names = {NH4:"nh4", CO:"co", CO2:"co2"}

class MQSensor(object):
    def __init__(self, gaz = MqGaz.NH4, cs_pin=board.D22, mcp_pin=MCP.P0, analog_scale=5., read_sample=5, read_interval=100,
                 calibration_sample=10, sample_interval=500, load_resistor=5):
        self.gaz=gaz
        self.gaz_name = MqGaz.names[gaz]
        self.to_concentration = MqResponse().laws[self.gaz]
        self.analog_scale = analog_scale
        self.read_interval = read_interval
        self.load_resistor = load_resistor
        self.read_sample = read_sample
        self.sample_interval = sample_interval
        self.spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        self.cs = digitalio.DigitalInOut(cs_pin)
        self.mcp = MCP.MCP3008(self.spi, self.cs)
        self.chan0 = AnalogIn(self.mcp, mcp_pin)
        self.calibration_sample = calibration_sample
        self._response_curves = ...
        self.clean_air_factor = 10  # TODO check in DataSheet
        self.r0 = 10

    def calibrate(self):
        vals = []
        for i in range(self.calibration_sample):
            vals.append(self._measure_resistance())
            time.sleep(self.sample_interval / 1000.)
        self.r0 = sum(vals) / len(vals) / self.clean_air_factor
        print("Calibration done")

    def _measure_adc(self):
        return self.chan0.voltage / self.analog_scale

    def _measure_resistance(self):
        adc = self._measure_adc()
        return self.load_resistor * (1 - adc) / adc

    def get_value(self):
        vals = []
        for i in range(self.read_sample):
            vals.append(self._measure_resistance())
        rs = self.load_resistor * sum(vals) / len(vals)
        ppm = self.to_concentration(rs/self.r0)
        raw = self._measure_adc()

        json_row = {"raw": raw, "ppm_"+self.gaz_name: ppm,'time': time.strftime("%d.%m.%Y %H:%M:%S"), "ts": time.time()}
        return json_row
