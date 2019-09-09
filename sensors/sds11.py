import os
import time
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

from __future__ import print_function
import serial, struct, sys, time, json, subprocess


class SDS_CONSTS:
    CMD_MODE = bytes([2])
    CMD_QUERY_DATA = bytes([4])
    CMD_DEVICE_ID = bytes([5])
    CMD_SLEEP = bytes([6])
    CMD_FIRMWARE = bytes([7])
    CMD_WORKING_PERIOD = bytes([8])
    MODE_ACTIVE = 0
    MODE_QUERY = 1
    PERIOD_CONTINUOUS = 0


class SDS(object):
    def __init__(self, port="/dev/ttyAMA0", baudrate=9600, DEBUG=False, VERBOSE=False):
        self.DEBUG = DEBUG
        self.VERBOSE = VERBOSE
        self.ser = serial.Serial()
        self.ser.port = "/dev/ttyAMA0"
        self.ser.baudrate = 9600
        self.ser.open()
        self.ser.flushInput()
        self.byte, self.data = 0, ""

    def dump(self, d, prefix=''):
        print(prefix + ' '.join(x.encode('hex') for x in d))

    def construct_command(self, cmd, data=[]):
        assert len(data) <= 12
        data += [0, ] * (12 - len(data))
        checksum = (sum(data) + cmd[0] - 2) % 256
        ret = b"\xaa\xb4" + cmd
        ret += bytes(data)
        ret += b"\xff\xff" + bytes([checksum]) + b"\xab"

        if self.DEBUG:
            self.dump(ret, '> ')
        return ret

    def process_data(self, d):
        r = struct.unpack('<HHxxBB', d[2:])
        pm25 = r[0] / 10.0
        pm10 = r[1] / 10.0
        checksum = sum(v for v in d[2:8]) % 256
        return [pm25, pm10]

    def process_version(self, d):
        r = struct.unpack('<BBBHBB', d[3:])
        checksum = sum(v for v in d[2:8]) % 256
        if self.VERBOSE:
            print("Y: {}, M: {}, D: {}, ID: {}, CRC={}".format(r[0], r[1], r[2], hex(r[3]),
                                                               "OK" if (checksum == r[4] and r[5] == 0xab) else "NOK"))

    def read_response(self):
        byte = 0
        while byte != b"\xaa":
            byte = self.ser.read(size=1)
        d = self.ser.read(size=9)
        if self.DEBUG:
            self.dump(d, '< ')
        return byte + d

    def cmd_set_mode(self, mode=SDS_CONSTS.MODE_QUERY):
        self.ser.write(self.construct_command(SDS_CONSTS.CMD_MODE, [0x1, mode]))
        return self.read_response()

    def cmd_query_data(self):
        self.ser.write(self.construct_command(SDS_CONSTS.CMD_QUERY_DATA))
        d = self.read_response()
        values = []
        if d[1] == 192:
            values = self.process_data(d)
        return values

    def cmd_set_sleep(self, sleep):
        mode = 0 if sleep else 1
        self.ser.write(self.construct_command(SDS_CONSTS.CMD_SLEEP, [0x1, mode]))
        return self.read_response()

    def cmd_set_working_period(self, period):
        self.ser.write(self.construct_command(SDS_CONSTS.CMD_WORKING_PERIOD, [0x1, period]))
        self.read_response()

    def cmd_firmware_ver(self):
        self.ser.write(self.construct_command(SDS_CONSTS.CMD_FIRMWARE))
        d = self.read_response()
        return self.process_version(d)

    def cmd_set_id(self, id):
        id_h = (id > > 8) % 256
        id_l = id % 256
        self.ser.write(self.construct_command(SDS_CONSTS.CMD_DEVICE_ID, [0] * 10 + [id_l, id_h]))
        self.read_response()

    def get_value(self):
        self.ser.timeout = .02
        self.cmd_set_sleep(0)
        time.sleep(2)
        self.cmd_set_working_period(SDS_CONSTS.PERIOD_CONTINUOUS)
        self.cmd_set_mode(SDS_CONSTS.MODE_QUERY)
        self.cmd_set_sleep(0)

        time.sleep(5)
        values = []
        for t in range(10):
            val = self.cmd_query_data()
            values.append(val)
        values = [v for v in values if v is not None and len(v) == 2]
        pm25 = [v[0] for v in values]
        pm10 = [v[1] for v in values]
        pm25 = sum(pm25) / len(pm25)
        pm10 = sum(pm10) / len(pm10)
        jsonrow = {'pm25': pm25, 'pm10': pm10, 'time': time.strftime("%d.%m.%Y %H:%M:%S"), "ts": time.time()}
        self.cmd_set_sleep(1)
        return jsonrow
