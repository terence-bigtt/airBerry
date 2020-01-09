import unittest
from persistance.diskwriter import DiskWriter, DiskWriterMessages
import os
from test.printlogger import PrintLogger


class TestDiskWriter(unittest.TestCase):
    def setUp(self):
        self.test_disk_actor = f'.disk_actor'
        self.test_disk = f'.disk'
        self.writer = DiskWriter(self.test_disk, 10, PrintLogger)
        self.actor = DiskWriter.start(self.test_disk_actor, 10, PrintLogger)

    def tearDown(self):
        if os.path.exists(self.test_disk):
            os.remove(self.test_disk)
        if os.path.exists(self.test_disk_actor):
            os.remove(self.test_disk_actor)
        self.actor.stop()

    def test_write(self):
        self.writer.write(dict(a=1))
        self.assertTrue(os.path.exists(self.test_disk))

    def test_read(self):
        self.writer.write(dict(a=2))
        self.assertNotEqual(self.writer.read(), dict(a=1))

    def test_buffersize(self):
        for i in range(20):
            self.writer.write(dict(b=i))
        self.assertEqual(len(self.writer.read()), self.writer.buffersize)

    def test_actor_write(self):
        self.actor.ask(DiskWriterMessages.Write(dict(c=1)))
        self.assertTrue(os.path.exists(self.test_disk_actor))

    def test_actor_read(self):
        self.actor.ask(DiskWriterMessages.Write(dict(c=2)))
        self.assertNotEqual(self.actor.ask(DiskWriterMessages.READ, timeout=1)[-1], dict(c=1))
