import adafruit_mcp3xxx.mcp3008 as MCP
import board
import busio
import digitalio
from adafruit_mcp3xxx.analog_in import AnalogIn
import time
import json
import os
import math


# TODO: Persist caliibration data

class MqResponse(object):
    def __init__(self):
        self._nh4pars = [(10, 2.6), (100, 1)]
        self._copars = [(10, 2.9), (100, 1.5)]
        self._co2pars = [(10, 2.15), (100, 1.1)]
        self.nh4 = self._power_law(self._nh4pars)
        self.co = self._power_law(self._copars)
        self.co2 = self._power_law(self._co2pars)
        self.laws = {MqGaz.NH4: self.nh4, MqGaz.CO: self.co, MqGaz.CO2: self.co2}

    def _power_law(self, pars):
        print("MQPowerLaw".format(self))
        exponent = math.log(pars[1][1] / pars[0][1]) / math.log(pars[1][0] / pars[0][0])
        return lambda x: pars[0][1] * math.pow((x / pars[0][0]), exponent)


class MqGaz:
    NH4 = 0
    CO = 1
    CO2 = 2

    names = {NH4: "nh4", CO: "co", CO2: "co2"}


class MQSensor(object):
    def __init__(self, gaz=MqGaz.NH4, cs_pin=board.D22, mcp_pin=MCP.P0, analog_scale=3.3, read_sample=5,
                 read_interval=100,
                 calibration_sample=10, sample_interval=500, load_resistor=5, cal_dir="."):
        self.gaz = gaz
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
        self._caldir = cal_dir
        self.r0 = None
        self._calfile = "mq-x.jsonl"
        self._read_calibration_data()
        self.calibration_history = []
        self.calibration = {}

    def _read_calibration_data(self):
        cal = {}
        try:
            with open(os.path.join(self._caldir, self._calfile), 'r') as f:
                self.calibration_history = [json.loads(line) for line in f.readlines()]
            self.calibration = self.calibration_history[-1]
        except:
            self.calibration_history = []
            self.calibration = {}
        self.r0 = self.calibration.get('r0', 10)

    def _write_calibration_data(self):
        with open(os.path.join(self._caldir, self._calfile), 'a') as f:
            data = {'ts': time.time(), 'r0': self.r0, 'device': "mq-x"}
            f.write(json.dumps(data) + '\n')
        self.calibration_history.append(data)
        self.calibration = data

    def calibrate(self):
        vals = []
        for i in range(self.calibration_sample):
            vals.append(self._measure_resistance())
            time.sleep(self.sample_interval / 1000.)

        vals = [v for v in vals if v is not None]
        if len(vals) != 0:
            self.r0 = sum(vals) / len(vals) / self.clean_air_factor
            self._write_calibration_data()
            return True

    def _measure_adc(self):
        adc = self.chan0.voltage / self.analog_scale
        print("{} - adc={}".format(self, adc))
        return adc

    def _measure_resistance(self):
        adc = self._measure_adc()
        if adc != 0:
            res=self.load_resistor * (1 - adc) / adc
            print("{} - resistance={}".format(self, adc))
            return res

    def get_value(self):
        print("{}-read".format(self))
        vals = []
        for i in range(self.read_sample):
            vals.append(self._measure_resistance())
        vals = [v for v in vals if v is not None]
        rs = sum(vals) / len(vals) if len(vals) != 0 else None
        ppm = self.to_concentration(rs / self.r0) if len(vals) != 0 else None
        raw = self._measure_adc() if len(vals) != 0 else None

        json_row = {"raw": raw, "ppm_" + self.gaz_name: ppm, 'time': time.strftime("%d.%m.%Y %H:%M:%S"),
                    "ts": time.time()}
        return json_row

    def __repr__(self):
        return "MQ135-{}".format(self.gaz)
