
class PrintLogger(object):
    @staticmethod
    def debug(*args, **kw):
        print(*args, *kw)

    @staticmethod
    def info(*args, **kw):
        print(*args, *kw)

    @staticmethod
    def warning(*args, **kw):
        print(*args, *kw)

    @staticmethod
    def error(*args, **kw):
        print(*args, *kw)