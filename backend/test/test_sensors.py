import unittest
from sensors.sensors import Sensors, Measure, SensorsMessages
from sensors.dummy import DummySensor
from test.printlogger import PrintLogger


class TestSensors(unittest.TestCase):
    def setUp(self):
        dummy = DummySensor(lag=0.5)
        dummy2 = DummySensor(lag=1)
        self.sensors = Sensors(PrintLogger, dummy, dummy2)
        self.actor = Sensors.start(PrintLogger, dummy, dummy2)

    def tearDown(self) -> None:
        self.actor.stop()

    def test_get_measures(self):
        values = self.sensors.get_values()
        self.assertEqual(type(values[0]), Measure)

    def test_parse_measure_default(self):
        values = self.sensors.get_values()
        raw = [v.format() for v in values]
        self.assertTrue("ts" in raw[0])

    def test_actor_read(self):
        values = self.actor.ask(SensorsMessages.READ)
        self.assertTrue(len(values) == 2)

    def test_actor_calibrate(self):
        self.assertTrue(self.actor.ask(SensorsMessages.CALIBRATE))

    def test_actor_calib_history(self):
        values = self.actor.ask(SensorsMessages.CALIBRATION_HISTORY)
        self.assertTrue(type(values) == list)


if __name__ == '__main__':
    unittest.main()
