import logging
import sys

# A set of standard LogRecord attributes to avoid adding them to the message
STANDARD_ATTRS = {
    'name',
    'levelno',
    'levelname',
    'pathname',
    'filename',
    'module',
    'funcName',
    'lineno',
    'created',
    'msecs',
    'relativeCreated',
    'thread',
    'threadName',
    'processName',
    'process',
    'message',
    'msg',
    'args',
    'exc_info',
    'exc_text',
    'stack_info',
    'extra',
    'taskName',
}


class DynamicExtraFilter(logging.Filter):
    def filter(self, record):
        extra_data = []
        for key, value in record.__dict__.items():
            if key not in STANDARD_ATTRS:
                extra_data.append(f'{key}: {value}')

        if extra_data:
            record.msg = f'{record.msg} | {" | ".join(extra_data)}'

        return True


def create_logger(name: str, log_level='DEBUG') -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    handler.addFilter(DynamicExtraFilter())
    logger.addHandler(handler)

    return logger
