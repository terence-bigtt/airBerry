import unittest
from unittest.mock import patch
from persistance.thingsboardwriter import TBWriter
from sensors.sensors import Measure
from test.printlogger import PrintLogger


class TestPostWriter(unittest.TestCase):
    def setUp(self) -> None:
        self.actor = TBWriter.start("http://url:9090", "token", ".test", PrintLogger)
        self.measure = Measure("key", 10, 100)

    def tearDown(self) -> None:
        self.actor.stop()

    @patch('persistance.postwriter.requests.post')
    def test_write_request(self, mock_post):
        inst = mock_post.return_value
        inst.status_code = 200
        res = self.actor.ask(self.measure)
        self.assertEqual(res, True)

    @patch('persistance.postwriter.requests.post')
    def test_consume_buffer(self, mock_post):
        inst = mock_post.return_value
        inst.status_code = 300
        self.actor.ask(self.measure)
        self.actor.ask(self.measure)
        inst.status_code = 200
        res = self.actor.ask(self.measure)
        self.assertEqual(res, True)

    def test_buffering(self):
        res = self.actor.ask(self.measure)
        self.assertEqual(res, False)


if __name__ == '__main__':
    unittest.main()
