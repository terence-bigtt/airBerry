import unittest
from unittest.mock import patch
from persistance.postwriter import PostWriter, WritePost
from test.printlogger import PrintLogger


class TestPostWriter(unittest.TestCase):
    def setUp(self) -> None:
        self.actor = PostWriter.start("url", ".test", PrintLogger)

    def tearDown(self) -> None:
        self.actor.stop()

    @patch('persistance.postwriter.requests.post')
    def test_write_request(self, mock_post):
        inst= mock_post.return_value
        inst.status_code=200
        res= self.actor.ask(WritePost({"k": "v"}))
        self.assertEqual(res, True)

    @patch('persistance.postwriter.requests.post')
    def test_consume_buffer(self, mock_post):
        inst = mock_post.return_value
        inst.status_code = 300
        self.actor.ask(WritePost({"k": "v1"}))
        self.actor.ask(WritePost({"k": "v2"}))
        inst.status_code = 200
        res = self.actor.ask(WritePost({"k": "v3"}))
        self.assertEqual(res, True)

    def test_buffering(self):
        res= self.actor.ask(WritePost({"k": "v"}))
        self.assertEqual(res, False)


if __name__ == '__main__':
    unittest.main()
