import logging.config


class InfoFilter(logging.Filter):
    """get message only from INFO tag"""

    def filter(self, message):
        return not (message.levelname == 'DEBUG') | \
                   (message.levelname == 'WARNING') | \
                   (message.levelname == 'ERROR') | \
                   (message.levelname == 'CRITICAL')
