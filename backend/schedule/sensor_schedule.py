from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import multiprocessing as mp


class SensorScheduler(object):
    def __init__(self, sensors, persistor):
        self.sensors = sensors
        self.persistor = persistor
        self.scheduler = BackgroundScheduler()
        self.schedule = None

    def read_and_reschedule(self, busy=None):
        self.persistor.logger.info("read and reschedule")
        self.persistor.logger.info(f"{busy.value}")
        self.persistor.logger.info(f"{self.schedule}")
        if self.schedule is not None:
            self.schedule.terminate()
            self.schedule.close()
        self.schedule = mp.Process(target=self._read_and_reschedule, args=(busy,))
        self.persistor.logger.info(f"{self.schedule}")

    def _read_and_reschedule(self, busy=None):
        self.persistor.logger.info(busy)
        if busy is not None:
            busy.value = True
        data = self.sensors.get_values()
        for datum in data:
            self.persistor.persist(datum)
        now = datetime.datetime.now()
        nextrun = now + datetime.timedelta(seconds=int(self.persistor.config.period_s))
        if busy is not None:
            busy.value = False
        self.scheduler.add_job(self._read_and_reschedule, 'date', next_run_time=nextrun)
