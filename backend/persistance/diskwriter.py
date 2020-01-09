from pykka import ThreadingActor, ThreadingFuture
from sensors.sensors import Measure
import json, os


class DiskWriterMessages(object):
    class Write(object):
        def __init__(self, message):
            self.message = message

    READ = "READ"
    POP = "POP"




class DiskWriterRequestRead(object):
    def __init__(self):
        pass


class DiskWriterPop(object):
    def __init__(self):
        pass


class DiskWriter(ThreadingActor):
    def __init__(self, filepath, buffersize, logger=None):
        ThreadingActor.__init__(self)
        self.buffersize = buffersize
        self.filepath = filepath
        self.logger = logger

    def on_receive(self, message):
        if message == DiskWriterMessages.READ:
            return self.read()

        if message == DiskWriterMessages.POP:
            return self.pop()

        if type(message) == DiskWriterMessages.Write:
            return self.write(message.message)

        if type(message) == Measure:
            self.write(message.format())

    def write(self, newdata):
        data = self.read()
        tokeep = (self.buffersize - 1) if self.buffersize > 0 else None
        data = [newdata] + data[:tokeep]
        with open(self.filepath, "w") as f:
            f.write("\n".join([json.dumps(d) for d in data]) + "\n")
        return True

    def pop(self):
        data = self.read()
        if len(data) > 0:
            popped = data[0]
            with open(self.filepath, "w+") as f:
                f.write("\n".join([json.dumps(d) for d in data[1:]]))
            return popped
        else:
            return None

    def read(self):
        data = []
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                lines = f.readlines()
            data = []
            for i, line in enumerate(lines):
                try:
                    data.append(json.loads(line))
                except Exception as e:
                    self.logger.error("failed to read line {i}")
                    self.logger.error(e.args)
        return data
