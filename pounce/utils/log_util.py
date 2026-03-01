import logging

import colorlog


class LoggingUtil():

    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

    def init_color_stream_handler(self):
        # 创建带颜色的日志格式
        formatter = colorlog.ColoredFormatter(
            fmt='%(log_color)s[%(asctime)s][%(levelname)s]%(message)s%(reset)s',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'bold_blue',
                'WARNING': 'bold_yellow',
                'ERROR': 'bold_red',
                'CRITICAL': 'bold_white,bg_red',
            },
            reset=True,
            style='%'
        )

        handler = colorlog.StreamHandler()
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)
        self.logger.addHandler(handler)

    def init_handlers(self):
        logging.getLogger('httpcore').setLevel(logging.WARNING)
        self.init_color_stream_handler()
