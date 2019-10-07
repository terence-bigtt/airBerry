from apscheduler.schedulers.background import BackgroundScheduler
import datetime


class SensorScheduler(object):
    def __init__(self, sensors, persistor):
        self.sensors = sensors
        self.persistor = persistor
        self.scheduler = BackgroundScheduler()

    def read_and_reschedule(self):
        data = self.sensors.get_values()
        for datum in data:
            self.persistor.persist(datum)
        now = datetime.datetime.now()
        nextrun = now + datetime.timedelta(seconds=int(self.persistor.config.period_s))
        self.scheduler.add_job(self.read_and_reschedule, 'date', next_run_time=nextrun)
