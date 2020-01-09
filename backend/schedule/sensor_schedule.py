from apscheduler.schedulers.background import BackgroundScheduler
from pykka._actor import ActorRef
import datetime
from sensors.sensors import SensorsMessages
from typing import List, Tuple
from configuration.configurator import Configurator
import os
from persistance.thingsboardwriter import TBWriter
from sensors.sensors import Sensors
from sensors.dummy import DummySensor
from persistance.diskwriter import DiskWriter, DiskWriterMessages

sensor_libs = True
try:
    from sensors.dht import DHT
    from sensors.sds11 import SDS
    from sensors.mq135 import MQSensor
except ImportError:
    sensor_libs = False


def make_persistors(config: Configurator, logger) -> Tuple[ActorRef, List[ActorRef]]:
    diskfile = os.path.join(config.fullpath, config.buffer_name)
    diskpersistor = DiskWriter.start(filepath=diskfile, buffersize=config.data_buffer, logger=logger)
    tbdiskfile = os.path.join(config.fullpath, "tb_temp.jsonl")
    tbpersistor = TBWriter.start(config.url_pattern, config.token, tbdiskfile, logger)
    return diskpersistor, [tbpersistor]


def make_sensors(config, logger) -> ActorRef:
    if sensor_libs:
        mq = MQSensor(cal_dir=config.fullpath)
        dht = DHT()
        sds = SDS(DEBUG=True)
        try:
            sds.cmd_set_sleep(1)
        except Exception as e:
            pass
        sensors = Sensors.start(logger, mq, dht, sds)
    else:
        dummy = DummySensor(caldir=config.fullpath)
        dummy2 = DummySensor(caldir=config.fullpath, name="dummy2")
        sensors = Sensors.start(logger, dummy, dummy2)
    return sensors


class SensorScheduler(object):
    def __init__(self, config, logger):
        diskpersistor, persistors = make_persistors(config, logger)
        self.config = config
        self.logger=logger
        self.period_s: int = config.period_s
        self.sensors: ActorRef = make_sensors(config, logger)
        self.persistors: List[ActorRef] = [diskpersistor] + persistors
        self.diskpersistor: ActorRef = diskpersistor
        self.scheduler = BackgroundScheduler()

    def start(self):
        self.scheduler.start()
        self.read_and_reschedule()

    def update(self, config):
        self.config.update(config)
        self.period_s = self.config.period_s
        self.diskpersistor, self.persistors = make_persistors(self.config, self.logger)

    def read_and_reschedule(self):
        data = self.sensors.ask(SensorsMessages.READ)
        for datum in data:
            for p in self.persistors:
                p.tell(datum)
        now = datetime.datetime.now()
        nextrun = now + datetime.timedelta(seconds=int(self.period_s))
        self.scheduler.add_job(self.read_and_reschedule, 'date', next_run_time=nextrun)
