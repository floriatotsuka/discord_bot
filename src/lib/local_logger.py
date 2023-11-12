from logging import getLogger, StreamHandler, config, INFO


class LocalLogger:
    def __init__(self, *, level=INFO):
        logger = getLogger(__name__)
        handler = StreamHandler()
        handler.setLevel(level)
        logger.setLevel(level)
        logger.addHandler(handler)
        logger.propagate = False
        self.logger = logger

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warn(self, msg):
        self.logger.warn(msg)

    def error(self, msg):
        self.logger.error(msg)

    def fatal(self, msg):
        self.logger.fatal(msg)
