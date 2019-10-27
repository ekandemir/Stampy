import time
import logging
import json

ELAPSED_TIME_PRECISION = 4


class Logger():
    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(name)

    def info(self, msg, **kwargs):
        kwargs.update({'msg': msg})
        self.logger.info(json.dumps(kwargs))

    def warn(self, msg, **kwargs):
        kwargs.update({'msg': msg})
        self.logger.warn(json.dumps(kwargs))

    def error(self, msg, **kwargs):
        kwargs.update({'msg': msg})
        self.logger.error(json.dumps(kwargs))


def getLogger(name):
    return Logger(name)


time_logger = getLogger('timings')


class Timer():
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __enter__(self):
        self.start = time.time()
        self.start_str = time.strftime('%H:%M:%S')
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.end_str = time.strftime('%H:%M:%S')
        elapsed_time = self.end - self.start
        time_logger.info(
            'Timer',
            start=self.start_str,
            end=self.end_str,
            elapsed_time=round(float(elapsed_time), ELAPSED_TIME_PRECISION),
            **self.kwargs)


def log_elapsed_time(method, **decorator_kwargs):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        ret = method(*args, **kwargs)
        elapsed_time = '{0:.2f}'.format(time.time() - start_time)
        method_name = '{}.{}'.format(method.__module__, method.__name__)
        logger_kwargs = {
            'elapsed_time': round(float(elapsed_time), ELAPSED_TIME_PRECISION),
            'method': method_name,
        }

        logger_kwargs.update(decorator_kwargs)
        time_logger.info('Timing in seconds', **logger_kwargs)

        return ret

    return wrapper
